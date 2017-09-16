"""Prediction Utility and constant classes."""

import functools
import json
import logging
import time
from google.appengine.api import memcache
from google.appengine.api import urlfetch


# pylint: disable=W0232,R0903
class Cache(object):

    """Cache decorator."""

    _CACHE_PREFIX = 'pg'

    def __init__(self, key, timeout=60,
                 is_cache_enabled=True, is_in_transaction=False):
        self.key = '%s:%s' % (self._CACHE_PREFIX, key)
        self.timeout = timeout
        self.is_cache_enabled = is_cache_enabled
        self.is_in_transaction = is_in_transaction

    def __call__(self, func):

        @functools.wraps(func)
        def wrapper(obj, *args, **kwargs):
            """Wrapper method to executed decorated method."""
            if not self.is_cache_enabled:
                return func(obj, *args, **kwargs)

            while True:
                cache_val = self._get_cache(self.key)
                if cache_val is not None:
                    if not self.is_in_transaction:
                        logging.info('Cache Hit, Key: %s', self.key)
                        return cache_val
                    else:
                        logging.info('Waiting...')
                        time.sleep(1)
                else:
                    break

            if self.is_in_transaction:
                self._set_cache(self.key, True)
            results = func(obj, *args, **kwargs)
            if self.is_in_transaction:
                self.remove()
            elif not self.is_in_transaction:
                self._set_cache(self.key, results)
            return results

        return wrapper

    def _set_cache(self, key, value):
        """Sets a cached value."""
        logging.info('Set Cache, Key: %s', key)
        memcache.set(key, value, self.timeout)

    def remove(self):
        """Remove a cached value."""
        cache_val = self._get_cache(self.key)
        if cache_val is not None:
            logging.info('Remove Cache, Key: %s', self.key)
            memcache.delete(self.key)

    @staticmethod
    def _get_cache(key):
        """Gets a cached value from either the per-request cache."""
        return memcache.get(key)


class InTransaction(object):

    """
    In Transaction, will help in making sure request completes after some
    retries.

    Usages:
        @InTransaction(retries=2)
        def some(text):
            print text
            return False
    """

    def __init__(self, retries=1):
        self.retries = retries

    def __call__(self, func):

        @functools.wraps(func)
        def wrapper(obj, *args, **kwargs):
            """Wrapper method to executed decorated method."""
            result = func(obj, *args, **kwargs)
            counter = 1
            while not result and counter < self.retries:
                logging.info('Retries...')
                logging.info(func)
                time.sleep(1 * counter)
                result = func(obj, *args, **kwargs)
                counter += 1
            return result

        return wrapper


def get_utf_str(message):
    """Return utf-8 encoded string."""
    try:
        return message.decode('utf-8').encode('utf-8')
    except UnicodeEncodeError as error:
        logging.warn(error)
    # pylint: disable=W0703
    except Exception as exp:
        logging.warn(exp)
    return message.encode('utf-8')


@InTransaction(retries=3)
def make_request(url, payload='', headers=None, method=urlfetch.GET):
    """Make http request."""
    headers = headers or {}
    if not headers.get('User-Agent'):
        headers.update(
            {'User-Agent': 'pgurin', 'Content-Type': 'application/json'})
    try:
        urlfetch.set_default_fetch_deadline(15)
        post_response = urlfetch.fetch(
            url=url,
            payload=payload,
            method=method,
            headers=headers,
            validate_certificate=True)
        if post_response.status_code in [200, 201]:
            # logging.info(post_response.content)
            if 'webhook' in url:
                return post_response.content
            return json.loads(post_response.content)
        logging.warn(
            'POST request Failed: %s, Payload: %s, Headers: %s, Status: %s',
            url, payload, headers, post_response.status_code)
    except Exception as exp:
        logging.warn(exp)
    return {}
