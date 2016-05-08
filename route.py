"""
  Route file.
"""

import appengine_config
import endpoints
import main
import webapp2
from background import ga_tasks, tasks, cron
from api.service import ShortUrlApi


APPLICATION = webapp2.WSGIApplication([
    webapp2.Route(
        '/_ah/queue/deferred', tasks.RunDeferred, name='deferredRun'),
    webapp2.Route(
        '/task/analytics', ga_tasks.GoogleAnalyticsHandler,
        name='AnalyticsTasks'),
    webapp2.Route(
        '/cron/removeip', cron.RemoveIPHandler, name='RemoveIP'),
    (r'/[\w\s\/]*', main.HomeHandler)
], config=appengine_config.CONFIG, debug=not appengine_config.IS_PROD)

API = endpoints.api_server(
    [ShortUrlApi],
    restricted=False
)
