import logging
import requests
import ckan.plugins.toolkit as toolkit


logger = logging.getLogger(__name__)


def make_tagger_get_request(endpoint, params=None):
    url = make_tagger_url(endpoint)
    return _make_generic_request(url, params=params)


def make_tagger_post_request(endpoint, json=None):
    url = make_tagger_url(endpoint)
    logger.debug('About to send the following JSON: ' + repr(json))
    return _make_generic_request(url, 'post', json=json)


def make_tagger_delete_request(endpoint, json=None):
    url = make_tagger_url(endpoint)
    logger.debug('About to send the following JSON: ' + repr(json))
    return _make_generic_request(url, 'delete', json=json)


def _make_generic_request(url, method='get', **kwargs):
    username, password = get_credentials()
    if username is not None and password is not None:
        auth = (username, password)
    else:
        auth = None

    logger.debug('Sending {} request to {}'.format(method, url))
    return getattr(requests, method)(
        url,
        timeout=29.,
        auth=auth,
        **kwargs
    )


def make_tagger_url(endpoint):
    return '{base}/api/v1/{config}{endpoint}'.format(
        base=get_tagger_base(),
        config=get_configuration(),
        endpoint=endpoint,
    )


def get_tagger_base():
    tagger_url = toolkit.config['ckan.dataontosearch.tagger_url']
    return tagger_url.rstrip('/')


def get_search_base():
    search_url = toolkit.config['ckan.dataontosearch.search_url']
    return search_url


def get_credentials():
    config = toolkit.config
    username = config.get('ckan.dataontosearch.username')
    password = config.get('ckan.dataontosearch.password')

    return username, password


def get_configuration():
    configuration = toolkit.config.get('ckan.dataontosearch.configuration')
    return configuration
