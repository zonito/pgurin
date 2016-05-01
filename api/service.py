"""ShortUrlApi API implemented using Google Cloud Endpoints."""

import appengine_config
import endpoints

from endpoints import api_config
from protorpc import remote
from api import service_impl
from api.proto_api import CreateRequest
from api.proto_api import GetRequest
from api.proto_api import RegisterRequest
from api.proto_api import Response

_AUTH_CONFIG = api_config.ApiAuth(allow_cookie_auth=True)


@endpoints.api(name='pgurin', version='v1',
               description='Prediction Short URL API',
               title='PGurin service',
               auth=_AUTH_CONFIG, owner_name='PredictionGuru',
               owner_domain='pgur.in')
class ShortUrlApi(remote.Service):

    """Class which defines pgurin API v1."""
    # pylint: disable=R0201
    @endpoints.method(RegisterRequest, Response,
                      path='register', name='pgur.register')
    def register(self, request):
        """
        Register device store url as well as default url in order to redirect,
        if no local application found or desktop / someother device browser.
        """
        success, reason, token = service_impl.register(request)
        return Response(success=success, reason=reason, token=token)

    @endpoints.method(RegisterRequest, Response,
                      path='update', name='pgur.update')
    def update(self, request):
        """
        Update device store url as well as default url in order to redirect,
        if no local application found or desktop / some other device browser.
        """
        success, reason = service_impl.update(request)
        return Response(success=success, reason=reason)

    @endpoints.method(CreateRequest, Response,
                      path='url/create', name='pgur.create')
    def url_create(self, request):
        """Create Short url from given details"""
        success, reason, url_uid = service_impl.create(request)
        if success:
            return Response(
                short_url=appengine_config.WEBSITE + url_uid,
                url_uid=url_uid, success=success)
        return Response(success=success, reason=reason)

    @endpoints.method(GetRequest, Response,
                      path='get', name='pgur.get')
    def get(self, request):
        """Return data from given ip address or url id."""
        success, reason, data = service_impl.get(request)
        return Response(success=success, reason=reason, data=data)
