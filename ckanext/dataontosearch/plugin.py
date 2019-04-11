import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import requests


# TODO: Use Unicode literals everywhere


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
            'dataontosearch_tagging_list_all': dataontosearch_tagging_list_all,
            'dataontosearch_tagging_list': dataontosearch_tagging_list,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'dataontosearch_concept_list': dataontosearch_concept_list_auth,
            'dataontosearch_tagging_list_all': dataontosearch_tagging_list_all_auth,
            'dataontosearch_tagging_list': dataontosearch_tagging_list_auth,
        }


@toolkit.side_effect_free
def dataontosearch_concept_list(context, data_dict):
    '''
    List concepts available from DataOntoSearch.

    :rtype: dict where key is a concept's URI, and value is a dict where the
        human-readable label is stored under 'label'.
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


@toolkit.side_effect_free
def dataontosearch_tagging_list_all(context, data_dict):
    '''
    List existing taggings for all datasets.

    :rtype: dictionary where key is ID of a dataset, and value is a list of
        concepts. Each concept is a dict, with 'label' being human-readable
        label and 'uri' being the URI identifying this concept.
    '''
    toolkit.check_access('dataontosearch_tagging_list_all', context, data_dict)
    r = make_tagger_get_request('/tagging')
    r.raise_for_status()

    data = r.json()

    taggings = dict()

    for uri, details in data.iteritems():
        # Try to extract the ID of this dataset
        dataset_id = uri.split('/')[-1]

        # Was this actually a URI for this CKAN?
        model = context['model']

        result = model.Package.get(dataset_id)
        if result:
            taggings[dataset_id] = details['concepts']

    return taggings


def dataontosearch_tagging_list_all_auth(context, data_dict):
    # Simply require users to be logged in
    return {
        'success': True
    }


@toolkit.side_effect_free
def dataontosearch_tagging_list(context, data_dict):
    '''
    List existing taggings for the specified dataset.

    :param id: id or name of the dataset to fetch taggings for
    :type id: string
    :rtype: list of concepts. Each concept is a dict, with 'label' being
        human-readable label and 'uri' being the URI identifying this concept
    '''
    toolkit.check_access('dataontosearch_tagging_list', context, data_dict)

    # Get the ID of this dataset
    dataset_id_or_name = toolkit.get_or_bust(data_dict, 'id')
    dataset = toolkit.get_action('package_show')(None, {'id': dataset_id_or_name})

    def get_data(dataset_id):
        dataset_uri = toolkit.url_for('dataset.read', id=dataset_id, _external=True)
        r = make_tagger_get_request('/tagging', {'dataset': dataset_uri})
        r.raise_for_status()

        data = r.json()
        return data

    # What URI is used in DataOntoSearch's RDF graph to identify this dataset?
    # It is usually the URL where the dataset can be seen, though it varies
    # whether the ID or name is used. Let's try the ID first.
    data = get_data(dataset['id'])

    if data is None:
        # Not the ID, try the name
        data = get_data(dataset['name'])

    if data is None:
        return []
    else:
        return data['concepts']


def dataontosearch_tagging_list_auth(context, data_dict):
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
