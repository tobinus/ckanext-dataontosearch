import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import requests


class DataOntoSearch_TaggingPlugin(plugins.SingletonPlugin):
    """
    Plugin for tagging datasets with relevant concepts.
    """
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'dataontosearch')

    # IActions

    def get_actions(self):
        return {
            'dataontosearch_concept_list': dataontosearch_concept_list,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'dataontosearch_concept_list': dataontosearch_concept_list_auth,
        }


@toolkit.side_effect_free
def dataontosearch_concept_list(context, data_dict):
    '''
    List concepts available from DataOntoSearch.

    :rtype: list of strings
    '''
    toolkit.check_access('dataontosearch_concept_list', context, data_dict)
    r = make_tagger_get_request('/concept')
    r.raise_for_status()

    data = r.json()

    return {
        uri: {'label': label} for uri, label in data.items()
    }


def dataontosearch_concept_list_auth(context, data_dict):
    # Simply require users to be logged in
    return {
        'success': True
    }


class DataOntoSearch_SearchingPlugin(plugins.SingletonPlugin):
    """
    Plugin for searching for datasets using semantic search in DataOntoSearch.
    """
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'dataontosearch')


def make_tagger_get_request(endpoint, params=None):
    url = '{base}/api/v1/{config}{endpoint}'.format(
        base=get_tagger_url(),
        config=get_configuration(),
        endpoint=endpoint,
    )
    return _make_generic_get_request(url, params)


def _make_generic_get_request(url, params=None):
    username, password = get_credentials()
    if username is not None and password is not None:
        auth = (username, password)
    else:
        auth = None

    return requests.get(
        url,
        params,
        timeout=29.,
        auth=auth,
    )


def get_tagger_url():
    tagger_url = toolkit.config['ckan.dataontosearch.tagger_url']
    return tagger_url


def get_search_url():
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
