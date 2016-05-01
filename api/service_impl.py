"""service implementation."""

import datetime
import json
import logging
import models
import random
import short_url


_NO_ACCOUNT = 'Account does not exists.'


def register(request):
    """Register new account."""
    token_int = int(datetime.datetime.strftime(
        datetime.datetime.now(), '%Y%m%d%H%M%S%f'))
    token = short_url.encode_url(token_int)
    if (not request.playstore_url and not request.appstore_url
            and not request.winstore_url and not request.default_url):
        return False, 'Insufficient information to register.', None
    account = models.Accounts(
        playstore_url=request.playstore_url,
        appstore_url=request.appstore_url,
        winstore_url=request.winstore_url,
        default_url=request.default_url,
        token=token
    )
    account.put()
    return True, None, token


def _get_account(token):
    """Return models.Accounts object."""
    return models.Accounts.query(models.Accounts.token == token).get()


def update(request):
    """Update account details."""
    account = _get_account(request.token)
    if not account:
        return False, _NO_ACCOUNT
    if request.playstore_url:
        account.playstore_url = request.playstore_url
    if request.appstore_url:
        account.appstore_url = request.appstore_url
    if request.winstore_url:
        account.winstore_url = request.winstore_url
    if request.default_url:
        account.default_url = request.default_url
    account.put()
    return True, None


def create(request):
    """Create short url"""
    if (not request.android_url and not request.ios_url
            and not request.windows_url and not request.other_url):
        return False, 'Insufficient information to create url', None
    account = _get_account(request.token)
    if not account:
        return False, _NO_ACCOUNT, None
    try:
        data = json.loads(request.data)
    except ValueError as error:
        logging.warn('ValueError: %s', error)
        return False, 'Invalid data object', None
    except TypeError as error:
        logging.warn('TypeError: %s', error)
        return False, 'Invalid data object', None
    if request.is_update:
        obj = models.ShortURLs.query(
            models.ShortURLs.url_id == request.url_uid).get()
        if not obj:
            return False, 'Invalid url id.', None
        obj.android_url = request.android_url
        obj.ios_url = request.ios_url
        obj.windows_url = request.windows_url
        obj.other_url = request.other_url
        obj.data = request.data
        obj.put()
        return True, None, request.url_uid
    obj = True
    url_uid = ''
    while obj:
        url_uid = short_url.encode_url(random.randint(1, 1000000000))
        logging.info('Trying ShortURL: %s', url_uid)
        obj = models.ShortURLs.query(models.ShortURLs.url_id == url_uid).get()
    obj = models.ShortURLs(
        url_id=url_uid,
        android_url=request.android_url,
        ios_url=request.ios_url,
        windows_url=request.windows_url,
        other_url=request.other_url,
        data=data,
        account=account
    )
    obj.put()
    return True, None, url_uid


def get(request):
    """Return data object from given ip / id."""
    account = _get_account(request.token)
    if not account:
        return False, _NO_ACCOUNT, None
    if request.url_uid:
        obj = models.ShortURLs.query(
            models.ShortURLs.url_id == request.url_uid
        ).get()
        if not obj:
            return False, 'Invalid URL Id', None
        return True, None, json.dumps(obj.data)
    if request.user_ip:
        ip_records = models.IPMapping.query(
            models.IPMapping.ip_address == request.user_ip
        ).order(-models.IPMapping.created).fetch(100)
        if not ip_records:
            return False, 'No Data available', None
        data = ip_records[0].short_url.data
        for ip_record in ip_records:
            ip_record.key.delete()
        return True, None, json.dumps(data)
    return False, 'Either IP Address or URL ID required.', None
