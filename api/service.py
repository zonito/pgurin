"""ShortUrlApi API implemented using Google Cloud Endpoints."""

import endpoints

from endpoints import api_config
from protorpc import remote
from api.proto_api import CreateRequest
from api.proto_api import UrlResponse
from api.proto_api import RegisterRequest
from api.proto_api import RegisterResponse

_AUTH_CONFIG = api_config.ApiAuth(allow_cookie_auth=True)


@endpoints.api(name='pgurin', version='v1',
               description='Prediction Short URL API',
               title='PGurin service',
               auth=_AUTH_CONFIG, owner_name='PredictionGuru',
               owner_domain='pgur.in')
class ShortUrlApi(remote.Service):

    """Class which defines pgurin API v1."""
    @endpoints.method(RegisterRequest, RegisterResponse,
                      path='register', name='pgur.register')
    def register(self, request):
        """
        Register device store url as well as default url in order to redirect,
        if no local application found or desktop / someother device browser.
        """
        return RegisterResponse(success=True)

    @endpoints.method(RegisterRequest, RegisterResponse,
                      path='update', name='pgur.update')
    def update(self, request):
        """
        Update device store url as well as default url in order to redirect,
        if no local application found or desktop / someother device browser.
        """
        return RegisterResponse(success=True)

    @endpoints.method(CreateRequest, UrlResponse,
                      path='create', name='pgur.create')
    def create(self, request):
        """
        Update device store url as well as default url in order to redirect,
        if no local application found or desktop / someother device browser.
        """
        return RegisterResponse(success=True)
