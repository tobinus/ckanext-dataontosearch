import logging
import ckan.plugins.toolkit as toolkit
try:
    from ckanext.dcat.utils import dataset_uri
except ImportError:
    raise RuntimeError(
        'ckanext-dataontosearch is dependent on ckanext-dcat, but could not '
        'find the latter'
    )

from ckanext.dataontosearch.utils import (
    make_tagger_get_request, make_tagger_delete_request,
    make_tagger_post_request
)

logger = logging.getLogger(__name__)


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
        'dataset_read',
        id=dataset_id,
        qualified=True
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


def dataontosearch_dataset_delete(context, data_dict):
    '''
    Remove all existing association between the specified dataset and concepts.

    This will also remove the dataset from DataOntoSearch's data store.

    :param id: Name or ID of the dataset to remove from DataOntoSearch
    :type id: string
    :return: True if the dataset was removed, or False if the dataset was not
        found.
    :rtype: bool
    '''
    toolkit.check_access('dataontosearch_dataset_delete', context, data_dict)

    # Extract parameters from data_dict
    dataset_id_or_name = toolkit.get_or_bust(data_dict, 'id')

    # What dataset is specified?
    dataset = toolkit.get_action('package_show')(None, {
        'id': dataset_id_or_name,
    })
    dataset_rdf_uri = dataset_uri(dataset)

    # Make the request
    r = make_tagger_delete_request('/dataset', {
        'dataset_id': dataset_rdf_uri,
    })
    r.raise_for_status()
    data = r.json()

    return data['success']


