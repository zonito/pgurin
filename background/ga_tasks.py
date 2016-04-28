"""
  Task file.
"""

import json
import logging
import utils
import webapp2

from pyanalytics.entities import Event, Page, Session, Tracker, Visitor
from pyanalytics.requests import Config


class GoogleAnalytics(object):

    """Google Analytics integration in server side."""

    wsgi_info = None
    post_data = None
    tracking_code = None
    domain = None
    response = None
    env = None

    def _get_page(self):
        """Return page object."""
        page = Page(self.env.get('PATH_INFO'))
        page.referrer = self.env.get('HTTP_REFERER', '/')
        page.load_time = int(self.wsgi_info.get('load_time', 0) * 1000)
        return page

    def _get_session(self):
        """Return session object."""
        session = Session()
        session.session_id = self.post_data.get('user_id', 0)
        return session

    def _get_tracker(self):
        """Get Tracker."""
        conf = Config()
        return Tracker(self.tracking_code, self.domain, conf=conf)

    def _get_visitor(self):
        """Return visitor object."""
        visitor = Visitor()
        visitor.user_agent = self.env.get('HTTP_USER_AGENT', 'Other!')
        visitor.locale = self.env.get(
            'HTTP_ACCEPT_LANGUAGE', 'en,en').split(',')[0]
        visitor.unique_id = int(self.post_data.get('user_id', 0))
        ip_address = self.env.get('REMOTE_ADDR', '1.0.0.0')
        visitor.ip_address = ip_address
        if self.post_data.get('private_key'):
            visitor.source = 'android'
        return visitor

    def _get_event(self, category=None, action=None, value=0):
        """Return event object."""
        private_key = self.post_data.get('private_key', 'web|x')
        api_type = self.env.get('PATH_INFO').replace(
            '/_ah/spi/', '').split('.')
        return Event(
            category=category or api_type[0],
            action=action or (api_type[1] if len(api_type) > 1 else ''),
            label=private_key.split('|')[0],
            value=value or self.wsgi_info.get('content-length', 0)
        )

    @utils.InTransaction(retries=3)
    def _track_event(self, category=None, action=None, value=1):
        """Global method for sending GA."""
        if category and action and value:
            try:
                tracker = self._get_tracker()
                tracker.track_event(
                    self._get_event(
                        category=category, action=action, value=value),
                    self._get_session(),
                    self._get_visitor(),
                    self._get_page()
                )
                return True
            except Exception as exp:
                logging.warning(exp)
                return False
        return True

    @utils.InTransaction(retries=3)
    def track_pageview(self):
        """Track required information per api request."""
        try:
            tracker = self._get_tracker()
            tracker.track_pageview(
                self._get_page(),
                self._get_session(),
                self._get_visitor()
            )
            return True
        except Exception as exp:
            logging.warning(exp)

    def track(self, wsgi_info, google_tracking_code, domain):
        """To track all required information, call deferred."""
        self.wsgi_info = wsgi_info
        self.env = self.wsgi_info.get('env')
        self.tracking_code = google_tracking_code
        self.domain = domain
        self.post_data = json.loads(wsgi_info.get('post_data'))
        self.response = json.loads(wsgi_info.get('response', '{}'))
        self._track_event()
        self.track_pageview()


class GoogleAnalyticsHandler(webapp2.RequestHandler):

    """GoogleAnalytics handler."""

    def post(self):
        """Handler request."""
        GoogleAnalytics().track(
            json.loads(self.request.get('wsgi_info')),
            self.request.get('code'),
            self.request.get('domain'))
        self.response.out.write('')
