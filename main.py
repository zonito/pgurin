"""
  Main file which is responsible to instantiate appengine application.
"""

import models
import os
import webapp2
from google.appengine.ext.webapp import template


class HomeHandler(webapp2.RequestHandler):

    """Displays redirect page."""

    def get(self):
        """GET request."""
        url_id = self.request.path[1:]
        if url_id:
            obj = models.ShortURLs.query(
                models.ShortURLs.url_id == url_id).get()
            if not obj:
                self.response.out.write('404 Page not found')
                return
            models.IPMapping(
                ip_address=os.environ['REMOTE_ADDR'],
                short_url=obj
            ).put()
            default_url = obj.account.default_url
            context = {
                'default_url': default_url,
                'android_url': obj.android_url or '',
                'playstore_url': obj.account.playstore_url or default_url,
                'ios_url': obj.ios_url or '',
                'appstore_url': obj.account.appstore_url or default_url,
                'windows_url': obj.windows_url or '',
                'winstore_url': obj.account.winstore_url or default_url
            }
            file_name = os.path.join(
                os.path.dirname(__file__), 'templates/index.html')
            content = template.render(file_name, context)
            self.response.headers['Content-Type'] = 'text/html'
            self.response.out.write(content)
            return
        self.response.out.write('OK')
