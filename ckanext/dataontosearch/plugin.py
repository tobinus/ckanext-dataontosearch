import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


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
    # TODO: Make actual request, instead of using example data
    return [
        {'uri': 'http://example.com/#more-testing', 'label': 'more testing'},
        {'uri': 'http://example.com/#yet-an-example', 'label': 'Yet another example'},
    ]


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
