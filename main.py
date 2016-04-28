"""
  Main file which is responsible to instantiate appengine application.
"""

import webapp2


class HomeHandler(webapp2.RequestHandler):

    """Displays redirect page."""

    def get(self):
        """GET request."""
        self.response.out.write('OK')
