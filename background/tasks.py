"""
  Task file.
"""

import webapp2
import logging

from google.appengine.ext import deferred


class RunDeferred(webapp2.RequestHandler):

    """Product handler."""

    def get(self):
        """Executes deferred tasks by invoking the deferred api handler."""
        try:
            deferred.run(self.request.raw_post_data)
        except deferred.PermanentTaskFailure as task_error:
            logging.exception(
                'Deferred Run failed.Exception: %s', task_error)
