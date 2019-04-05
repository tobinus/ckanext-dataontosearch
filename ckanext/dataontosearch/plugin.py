from ckan.common import config
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class DataOntoSearch_TaggingPlugin(plugins.SingletonPlugin):
    """
    Plugin for tagging datasets with relevant concepts.
    """
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'dataontosearch')


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
    tagger_url = config['ckan.dataontosearch.tagger_url']
    return tagger_url


def get_search_url():
    search_url = config['ckan.dataontosearch.search_url']
    return search_url


def get_credentials():
    username = config.get('ckan.dataontosearch.username')
    password = config.get('ckan.dataontosearch.password')

    return username, password


def get_configuration():
    configuration = config.get('ckan.dataontosearch.configuration')
    return configuration
