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


class CreateRequest(messages.Message):

    """Request to create short url"""
    android_url = messages.StringField(1)
    ios_url = messages.StringField(2)
    windows_url = messages.StringField(3)
    token = messages.StringField(4)


class UrlResponse(messages.Message):

    """Response with short url."""
    short_url = messages.StringField(1, required=True)
    url_uid = messages.StringField(2, required=True)
