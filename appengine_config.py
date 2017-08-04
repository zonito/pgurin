"""
Configuration / Constants for the application.
"""
import json
import logging
import os
import time

from google.appengine.api import taskqueue
from google.appengine.ext import vendor

vendor.add('lib')

CONFIG = {}
CONFIG['webapp2_extras.sessions'] = dict(secret_key='pgurin')
_APP_ID = os.environ.get('APPLICATION_ID', '')
IS_PROD = 'pgur-in' in _APP_ID
IS_LOCAL = _APP_ID.startswith('dev~')
WEBSITE = 'http://pgur.in/'

# pylint: disable=C0103
remoteapi_CUSTOM_ENVIRONMENT_AUTHENTICATION = (
    'HTTP_X_APPENGINE_INBOUND_APPID', ['pgur-in']
)

# Google Analytics
DOMAIN = 'appspot.com'
GOOGLE_TRACKING_CODE = 'UA-68498210-4'


def webapp_add_wsgi_middleware(app):
    """
    To enable /_ah/stats for tracking purpose.
    """

    def google_analytics_middleware(app):
        """Middleware to send request flow details in google analytis."""

        def google_analytics_middleware_wrapper(environ, start_response):
            """Wrapper method to get more detailed information."""
            path = environ.get('PATH_INFO', '')
            is_api_call = (
                '/_ah/spi/' in path and '/_ah/spi/BackendService' not in path)
            wsgi_info = {}
            start_time = time.time()
            if is_api_call:
                from cStringIO import StringIO
                length = 0
                try:
                    length = int(environ.get('CONTENT_LENGTH'))
                except TypeError as error:
                    logging.warning(error)
                post_data = environ['wsgi.input'].read(length)
                environ['wsgi.input'] = StringIO(post_data)
                wsgi_info = {
                    'env': environ,
                    'post_data': post_data
                }

            def appstats_start_response(status, headers, exc_info=None):
                """
                Wrapper of wrapper method, again for more detailed information.
                """
                wsgi_info['status'] = status
                return start_response(status, headers, exc_info)
            try:
                result = app(environ, appstats_start_response)
                wsgi_info['load_time'] = time.time() - start_time
            except Exception:
                raise
            if result is not None:
                for value in result:
                    wsgi_info['content-length'] = len(value)
                    wsgi_info['response'] = value
                    yield value
            if wsgi_info.get('status') == '200 OK' and is_api_call:
                del wsgi_info['env']['wsgi.input']
                del wsgi_info['env']['wsgi.errors']
                del wsgi_info['env']['google.api.config.service']
                del wsgi_info['env']['google.api.config.method_registry']
                del wsgi_info['env']['google.api.config.reporting_rules']
                del wsgi_info['env']['google.api.config.method_info']
                try:
                    taskqueue.add(
                        url='/task/analytics',
                        params={'wsgi_info': json.dumps(wsgi_info),
                                'code': GOOGLE_TRACKING_CODE,
                                'domain': DOMAIN},
                        queue_name='googleanalytics'
                    )
                except taskqueue.TaskTooLargeError as ttle:
                    logging.debug(ttle)
        return google_analytics_middleware_wrapper

    app = google_analytics_middleware(app)
    # from google.appengine.ext.appstats import recording
    # if not IS_LOCAL:
    #     app = recording.appstats_wsgi_middleware(app)
    return app
