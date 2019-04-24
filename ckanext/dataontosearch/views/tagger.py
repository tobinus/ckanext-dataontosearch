# encoding: utf-8
import logging
import functools
import ckan.plugins.toolkit as toolkit

from flask import Blueprint

logger = logging.getLogger(__name__)

tagger = Blueprint(
    u'dataontosearch_tagger',
    __name__,
    url_prefix=u'/dataontosearch/tagger/<dataset_id>'
)


def _log_exceptions(f):
    '''
    Log any exception that occurs while running the decorated function.
    '''
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            logger.exception(u'Exception occurred while processing route')
            raise
    return wrapper


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


@tagger.route(u'/')
@_log_exceptions
@_with_dataset
def show(dataset_dict, context):
    # Fetch tags for the dataset
    data_dict = {u'id': dataset_dict[u'id']}
    concepts = toolkit.get_action(u'dataontosearch_tag_list')(
        context,
        data_dict
    )

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
        can_edit = True
    except toolkit.Notauthorized:
        logger.debug(u'User cannot edit concepts')
        can_edit = False

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
    # TODO: Perhaps reduce the amount of duplication a bit?
    # Fetch tags for the dataset
    data_dict = {u'id': dataset_dict[u'id']}
    existing_concepts = toolkit.get_action(u'dataontosearch_tag_list')(
        context,
        data_dict
    )

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
        can_edit = True
    except toolkit.Notauthorized:
        can_edit = False
    # End copied code

    if not can_edit:
        return toolkit.abort(
            401,
            toolkit._(u'You are not allowed to edit concepts associated with '
                      u'this dataset')
        )

    # TODO: Implement editing (adding, removing) concepts
    return toolkit.abort(500, u'Editing is not implemented yet')
