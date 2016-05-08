"""Cron Jobs"""

import webapp2
import datetime
import models


class RemoveIPHandler(webapp2.RequestHandler):

    """Copy remove ip address records after 2 days."""

    def get(self):
        """Remove data after 2 days."""
        delta = datetime.datetime.today() - datetime.timedelta(days=2)
        ip_records = models.IPMapping.query(
            models.IPMapping.created < delta
        ).fetch(1000)
        for record in ip_records:
            record.key.delete()
        self.response.out.write('OK')
