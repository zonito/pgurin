"""ProtoRPC message class definitions for Prediction API."""

from protorpc import messages


class RegisterRequest(messages.Message):

    """Structure to register application and get token."""
    playstore_url = messages.StringField(1)
    appstore_url = messages.StringField(2)
    winstore_url = messages.StringField(3)
    default_url = messages.StringField(4)
    # In case of update request
    token = messages.StringField(5)


class RegisterResponse(messages.Message):

    """Response with token once registered."""
    success = messages.BooleanField(1, required=True)
    reason = messages.StringField(2)
    token = messages.StringField(3, required=True)


class StoreIPRequest(messages.Message):

    """Store IP address when user click link."""
    ip_address = messages.StringField(1, required=True)


class CreateRequest(messages.Message):

    """Request to create short url"""
    token = messages.StringField(1, required=True)
    android_url = messages.StringField(2)
    ios_url = messages.StringField(3)
    windows_url = messages.StringField(4)
    other_url = messages.StringField(5)
    data = messages.StringField(6)


class UrlResponse(messages.Message):

    """Response with short url."""
    short_url = messages.StringField(1, required=True)
    url_uid = messages.StringField(2, required=True)


class GetRequest(messages.Message):

    """Get request."""
    token = messages.StringField(1, required=True)
    url_uid = messages.StringField(2)
    user_ip = messages.StringField(3)


class GetResponse(messages.Message):

    """Return data from given id / ip"""
    data = messages.StringField(1, required=True)
