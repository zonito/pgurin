"""
  Main file which is responsible to instantiate appengine application.
"""

import appengine_config
import json
import logging
import models
import os
import urllib
import utils
import webapp2
from google.appengine.api import taskqueue
from google.appengine.ext.webapp import template


_PG_API_URL = 'https://dev-dot-prediction-prd.appspot.com/_ah/api/prediction/v1'


def _send_to_ga(url_id, ip_address, token):
    """Send visits to GA for tracking."""
    try:
        wsgi_info = {
            'env': {
                'PATH_INFO': '/redirect/' + url_id,
                'REMOTE_ADDR': ip_address
            },
            'response': json.dumps({'url_uid': url_id}),
            'post_data': json.dumps({'token': token})
        }
        taskqueue.add(
            url='/task/analytics',
            params={'wsgi_info': json.dumps(wsgi_info),
                    'code': appengine_config.GOOGLE_TRACKING_CODE,
                    'domain': appengine_config.DOMAIN}
        )
    except taskqueue.TaskTooLargeError as ttle:
        logging.debug(ttle)
    return True


class HomeHandler(webapp2.RequestHandler):

    """Displays redirect page."""
    @staticmethod
    def get_group_urlid(url_id):
        """Return group url id"""
        @utils.Cache('group:%s' % url_id, 3600 * 24)
        def wrapper(url_id):
            """For cache"""
            payload = {'user_id': 0, 'recid': url_id}
            response = utils.make_request(
                _PG_API_URL + '/group/referral', json.dumps(payload),
                method='POST')
            logging.info(response)
            if response.get('success'):
                url_id = response.get('reason')
            return url_id
        return wrapper(url_id)

    def update_ga(self, obj):
        """Return False, if request is from bot."""
        user_agent = self.request.headers.get('User-Agent', '..').lower()
        is_bot = False
        for bot in ['applebot', 'slurp', 'dataminr', 'fb_iab']:
            if bot in user_agent:
                is_bot = True
        if not is_bot:
            ip_address = os.environ['REMOTE_ADDR']
            models.IPMapping(
                ip_address=ip_address,
                short_url=obj
            ).put()
            logging.info(ip_address)
            _send_to_ga(obj.url_id, ip_address, obj.account.token)
        return is_bot

    def get(self):
        """GET request."""
        url_id = self.request.path[1:]
        utm_term = 'normal'
        medium = 'app'
        if 'group/' in url_id:
            logging.info('GroupLink: %s', url_id)
            medium = url_id.replace('group/', '')
            utm_term = 'group'
            url_id = self.get_group_urlid(medium)
        if url_id:
            obj = models.ShortURLs.query(
                models.ShortURLs.url_id == url_id).get()
            if not obj:
                self.response.out.write('404 Page not found')
                return
            self.update_ga(obj)
            default_url = obj.account.default_url
            playstore_url = obj.account.playstore_url or default_url
            utm_query = urllib.urlencode(
                dict(
                    utm_source='pgurin',
                    utm_content=url_id,
                    utm_medium=medium,
                    utm_campaign='referral',
                    utm_term=utm_term
                )
            )
            playstore_url = playstore_url + '&' + utm_query
            params = urllib.urlencode(
                dict(link=playstore_url, apn='com.guru.prediction'))
            playstore_url = ('https://drfa7.app.goo.gl/?' + params)
            logging.info(playstore_url)
            context = dict(
                default_url=default_url,
                android_url=obj.android_url or '',
                playstore_url=playstore_url,
                ios_url=obj.ios_url or '',
                appstore_url=obj.account.appstore_url or default_url,
                windows_url=obj.windows_url or '',
                winstore_url=obj.account.winstore_url or default_url,
                description=obj.account.description,
                title=obj.account.title,
                banner=obj.account.banner,
                delay=obj.delay
            )
            file_name = os.path.join(
                os.path.dirname(__file__), 'templates/index.html')
            content = template.render(file_name, context)
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(content)
            return
        self.response.out.write('OK')
