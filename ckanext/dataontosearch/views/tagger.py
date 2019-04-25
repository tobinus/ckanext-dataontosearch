# encoding: utf-8
import logging
import functools
import ckan.plugins.toolkit as toolkit

from flask import Blueprint

from ckanext.dataontosearch.views.utils import _log_exceptions

logger = logging.getLogger(__name__)

tagger = Blueprint(
    u'dataontosearch_tagger',
    __name__,
    url_prefix=u'/dataontosearch/tagger/<dataset_id>'
)


def _with_dataset(f):
    '''
    For routes receiving dataset_id, this will transform that into dataset_dict.

    The CKAN context is additionally given in as context.

    A redirect is issued if the user used the ID and not the dataset name, since
    we want to be consistent in which URL we use and not allow two names for the
    same dataset.
    '''
    @functools.wraps(f)
    def wrapper(dataset_id, *args, **kwargs):
        context = {}

        # Fetch info about the dataset
        data_dict = {u'id': dataset_id}
        try:
            dataset_dict = toolkit.get_action(u'package_show')(context, data_dict)
        except (toolkit.ObjectNotFound, toolkit.NotAuthorized):
            return toolkit.abort(404, toolkit._(u'Dataset not found'))

        # If the user specified a dataset id, redirect to the dataset name
        # (having one canonical URL is good to avoid caching multiple times etc)
        id_was_used = dataset_id == dataset_dict[u'id']
        name_was_used = dataset_id == dataset_dict[u'name']
        if id_was_used and not name_was_used:
            return toolkit.redirect_to(
                u'dataontosearch_tagger.{}'.format(f.__name__),
                dataset_id=dataset_dict[u'name']
            )

        # Let the route do the rest, now with the dataset_dict and context
        return f(*args, dataset_dict=dataset_dict, context=context, **kwargs)

    return wrapper


def _with_can_edit(f):
    '''
    Check whether the given dataset_dict can be edited by the user, in can_edit.
    '''
    @functools.wraps(f)
    def wrapper(context, dataset_dict, *args, **kwargs):
        can_edit = _get_can_edit(context, dataset_dict)
        return f(
            *args,
            dataset_dict=dataset_dict,
            context=context,
            can_edit=can_edit,
            **kwargs
        )
    return wrapper


def _get_can_edit(context, dataset_dict):
    # Can the tags be edited?
    try:
        toolkit.check_access(
            u'dataontosearch_tag_create',
            context,
            {
                u'dataset': dataset_dict[u'id'],
                u'concept': u'http://example.com/rdf#Example',
            }
        )
        return True
    except toolkit.Notauthorized:
        logger.debug(u'User cannot edit concepts')
        return False


def _get_existing_tags(context, dataset_dict):
    data_dict = {u'id': dataset_dict[u'id']}
    return toolkit.get_action(u'dataontosearch_tag_list')(
        context,
        data_dict
    )


@tagger.route(u'/')
@_log_exceptions
@_with_dataset
@_with_can_edit
def show(context, dataset_dict, can_edit):
    # Fetch tags for the dataset
    concepts = _get_existing_tags(context, dataset_dict)

    # Render the page
    return toolkit.render(
        u'dataontosearch_tagger_show.html',
        {
            u'dataset': dataset_dict,
            u'concepts': concepts,
            u'can_edit': can_edit,
        }
    )


@tagger.route(u'/edit', methods=[u'GET', u'POST'])
@_log_exceptions
@_with_dataset
def edit(dataset_dict, context):
    # Fetch tags for the dataset
    existing_concepts = _get_existing_tags(context, dataset_dict)

    if not _get_can_edit(context, dataset_dict):
        return toolkit.abort(
            401,
            toolkit._(u'You are not allowed to edit concepts associated with '
                      u'this dataset')
        )

    # TODO: Implement editing (adding, removing) concepts
    return toolkit.abort(500, u'Editing is not implemented yet')
