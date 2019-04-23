# encoding: utf-8
import logging
import requests
import ckan.plugins.toolkit as toolkit


logger = logging.getLogger(__name__)


def make_tagger_get_request(endpoint, params=None):
    url = make_tagger_url(endpoint)
    return _make_generic_request(url, params=params)


def make_tagger_post_request(endpoint, json=None):
    url = make_tagger_url(endpoint)
    logger.debug(u'About to send the following JSON: ' + repr(json))
    return _make_generic_request(url, u'post', json=json)


def make_tagger_delete_request(endpoint, json=None):
    url = make_tagger_url(endpoint)
    logger.debug(u'About to send the following JSON: ' + repr(json))
    return _make_generic_request(url, u'delete', json=json)


def make_search_get_request(endpoint, params=None):
    url = make_search_url(endpoint)

    # Inject configuration parameter
    if params is None:
        params = {u'c': get_configuration()}
    else:
        params[u'c'] = get_configuration()

    return _make_generic_request(url, params=params)


def _make_generic_request(url, method=u'get', **kwargs):
    username, password = get_credentials()
    if username is not None and password is not None:
        auth = (username, password)
    else:
        auth = None

    logger.debug(u'Sending {} request to {}'.format(method, url))
    return getattr(requests, method)(
        url,
        timeout=29.,
        auth=auth,
        **kwargs
    )


def make_tagger_url(endpoint):
    return u'{base}/api/v1/{config}{endpoint}'.format(
        base=get_tagger_base(),
        config=get_configuration(),
        endpoint=endpoint,
    )


def get_tagger_base():
    tagger_url = toolkit.config[u'ckan.dataontosearch.tagger_url']
    return tagger_url.rstrip(u'/')


def make_search_url(endpoint):
    return u'{base}/api/v1{endpoint}'.format(
        base=get_search_base(),
        endpoint=endpoint
    )


def get_search_base():
    search_url = toolkit.config[u'ckan.dataontosearch.search_url']
    return search_url.rstrip(u'/')


def get_credentials():
    config = toolkit.config
    username = config.get(u'ckan.dataontosearch.username')
    password = config.get(u'ckan.dataontosearch.password')

    return username, password


def get_configuration():
    configuration = toolkit.config.get(u'ckan.dataontosearch.configuration')
    return configuration


def get_use_autotag():
    use_autotag = toolkit.config.get(u'ckan.dataontosearch.use_autotag', False)
    return toolkit.asbool(use_autotag)
