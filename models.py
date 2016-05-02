"""Models / Schema of pgur.in"""

from google.appengine.ext import ndb


class Accounts(ndb.Model):

    """Stores registration information."""
    playstore_url = ndb.StringProperty()
    appstore_url = ndb.StringProperty()
    winstore_url = ndb.StringProperty()
    default_url = ndb.StringProperty()
    title = ndb.StringProperty(required=True)
    banner = ndb.StringProperty(required=True)
    description = ndb.TextProperty()
    token = ndb.StringProperty(required=True, indexed=True)


class ShortURLs(ndb.Model):
    """Stores shorten url for given app links."""
    url_id = ndb.StringProperty(indexed=True)
    android_url = ndb.StringProperty()
    ios_url = ndb.StringProperty()
    windows_url = ndb.StringProperty()
    other_url = ndb.StringProperty()
    data = ndb.JsonProperty(required=True)
    account = ndb.StructuredProperty(Accounts, required=True)
    created = ndb.DateTimeProperty(auto_now=True)


class IPMapping(ndb.Model):
    """Stores IP-UID mapping."""
    ip_address = ndb.StringProperty(required=True, indexed=True)
    short_url = ndb.StructuredProperty(ShortURLs, required=True)
    created = ndb.DateTimeProperty(auto_now=True)
