"""ShortUrlApi API implemented using Google Cloud Endpoints."""

import endpoints

from endpoints import api_config
from protorpc import remote

_AUTH_CONFIG = api_config.ApiAuth(allow_cookie_auth=True)


@endpoints.api(name='pgurin', version='v1',
               description='Prediction Short URL API',
               title='PGurin service',
               auth=_AUTH_CONFIG, owner_name='PredictionGuru',
               owner_domain='pgur.in')
class ShortUrlApi(remote.Service):

    """Class which defines pgurin API v1."""
