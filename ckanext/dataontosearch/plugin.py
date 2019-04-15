import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
try:
    from ckanext.dcat.utils import dataset_uri
except ImportError:
    raise RuntimeError(
        'ckanext-dataontosearch is dependent on ckanext-dcat, but could not '
        'find the latter'
    )
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
            'dataontosearch_tagging_create': dataontosearch_tagging_create,
            'dataontosearch_tagging_delete': dataontosearch_tagging_delete,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'dataontosearch_concept_list': dataontosearch_concept_list_auth,
            'dataontosearch_tagging_list_all': dataontosearch_tagging_list_all_auth,
            'dataontosearch_tagging_list': dataontosearch_tagging_list_auth,
            'dataontosearch_tagging_create': dataontosearch_tagging_create_auth,
            'dataontosearch_tagging_delete': dataontosearch_tagging_delete_auth,
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

    # What dataset is specified?
    dataset_id_or_name = toolkit.get_or_bust(data_dict, 'id')
    dataset = toolkit.get_action('package_show')(None, {'id': dataset_id_or_name})

    # Generate the RDF URI for this dataset, using the very same code used by
    # ckanext-dcat. We need this to be consistent with what DataOntoSearch found
    # when it retrieved the dataset RDF, thus this use of the internal DCAT API.
    dataset_rdf_uri = dataset_uri(dataset)

    r = make_tagger_get_request('/tagging', {'dataset_id': dataset_rdf_uri})
    r.raise_for_status()

    data = r.json()

    if data is None:
        return []
    else:
        return data['concepts']


def dataontosearch_tagging_list_auth(context, data_dict):
    # Simply require users to be logged in
    return {
        'success': True
    }


def dataontosearch_tagging_create(context, data_dict):
    '''
    Create a new association between the specified dataset and concept.

    :param dataset: Name or ID of the dataset to associate with a concept
    :type dataset: string
    :param concept: RDF URI or human-readable label for the concept to associate
        with the dataset
    :type dataset: string
    :return: The dataset, concept and id for the newly created tagging
    :rtype: dictionary
    '''
    toolkit.check_access('dataontosearch_tagging_create', context, data_dict)

    # Extract parameters from data_dict
    dataset_id_or_name = toolkit.get_or_bust(data_dict, 'dataset')
    concept_url_or_label = toolkit.get_or_bust(data_dict, 'concept')

    # We must provide DataOntoSearch with a URL of where to download metadata,
    # so generate this URL. First, what dataset was specified?
    dataset = toolkit.get_action('package_show')(
        None,
        {'id': dataset_id_or_name}
    )

    # We assume the RDF is available at the usual dataset URL, but with a
    # .rdf suffix
    dataset_id = dataset.get('id')
    dataset_url = toolkit.url_for(
        'dataset.read',
        id=dataset_id,
        _external=True
    )
    rdf_url = '{}.rdf'.format(dataset_url)

    # Now we are equipped to actually create the tagging
    r = make_tagger_post_request(
        '/tagging',
        {
            'dataset_url': rdf_url,
            'concept': concept_url_or_label,
        }
    )
    r.raise_for_status()

    # Handle response
    data = r.json()

    if not data['success']:
        raise RuntimeError(data['message'])

    return {
        'dataset': dataset_id,
        'concept': concept_url_or_label,
        'id': data['id'],
    }


def dataontosearch_tagging_create_auth(context, data_dict):
    # TODO: Don't let people do tagging unless they can edit datasets and such
    # We allow anyone who is logged in
    return {
        'success': True
    }


def dataontosearch_tagging_delete(context, data_dict):
    '''
    Remove an existing association between the specified dataset and concept.

    :param dataset: Name or ID of the dataset to disassociate with a concept
    :type dataset: string
    :param concept: RDF URI or human-readable label for the concept to no longer
        associate with the dataset
    :type dataset: string
    :return: True
    :rtype: bool
    '''
    toolkit.check_access('dataontosearch_tagging_delete', context, data_dict)

    # Extract parameters from data_dict
    dataset_id_or_name = toolkit.get_or_bust(data_dict, 'dataset')
    concept_url_or_label = toolkit.get_or_bust(data_dict, 'concept')

    # What dataset is specified?
    dataset = toolkit.get_action('package_show')(None, {
        'id': dataset_id_or_name,
    })
    dataset_rdf_uri = dataset_uri(dataset)

    # Make the request
    r = make_tagger_delete_request('/tagging', {
        'dataset_id': dataset_rdf_uri,
        'concept': concept_url_or_label,
    })
    r.raise_for_status()
    data = r.json()

    return data['success']


def dataontosearch_tagging_delete_auth(context, data_dict):
    # TODO: Don't let people remove tagging unless they can add tagging
    # Allow anyone who is logged in
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
    url = make_tagger_url(endpoint)
    return _make_generic_request(url, params=params)


def make_tagger_post_request(endpoint, json=None):
    url = make_tagger_url(endpoint)
    return _make_generic_request(url, 'post', json=json)


def make_tagger_delete_request(endpoint, json=None):
    url = make_tagger_url(endpoint)
    return _make_generic_request(url, 'delete', json=json)


def _make_generic_request(url, method='get', **kwargs):
    username, password = get_credentials()
    if username is not None and password is not None:
        auth = (username, password)
    else:
        auth = None

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
