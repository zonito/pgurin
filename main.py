"""
  Main file which is responsible to instantiate appengine application.
"""

import os
import webapp2
from google.appengine.ext.webapp import template


class HomeHandler(webapp2.RequestHandler):

    """Displays redirect page."""

    def get(self):
        """GET request."""
        short_url = self.request.path[1:]
        self.response.headers['Content-Type'] = 'text/html'
        file_name = os.path.join(
            os.path.dirname(__file__), 'templates/index.html')
        content = template.render(file_name, {'url': short_url})
        self.response.out.write(content)
