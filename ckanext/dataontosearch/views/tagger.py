# encoding: utf-8
import logging
import functools
import ckan.plugins.toolkit as toolkit

from flask import Blueprint, request
from requests.exceptions import RequestException

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
    except toolkit.NotAuthorized:
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
    is_submitted = request.method == u'POST'
    empty_value = u'NONE'
    error = None

    if is_submitted:
        new_tag_list = request.form.getlist(u'new_concept[]')
        existing_tag_list = request.form.getlist(u'existing_concept[]')

        new_tag_set = set(new_tag_list)
        new_tag_set.discard(empty_value)
        existing_tag_set = set(existing_tag_list)


        added_tags = new_tag_set - existing_tag_set
        removed_tags = existing_tag_set - new_tag_set

        # TODO: Make this operation more atomic, not partially applied if error
        # We add concepts first, since that's less destructive in case of error
        try:
            add_action = toolkit.get_action(u'dataontosearch_tag_create')
            for new_concept in added_tags:
                add_action(context, {
                    u'dataset': dataset_dict[u'id'],
                    u'concept': new_concept,
                })

            remove_action = toolkit.get_action(u'dataontosearch_tag_delete')
            for removed_concept in removed_tags:
                remove_action(context, {
                    u'dataset': dataset_dict[u'id'],
                    u'concept': removed_concept,
                })
        except (
                toolkit.NotAuthorized,
                toolkit.ObjectNotFound,
                toolkit.ValidationError,
                RequestException
        ) as e:
            logger.exception(
                u'Failed to process edit of concepts for %s',
                dataset_dict[u'id']
            )
            error = str(e)

        # Redirect back (as GET request)
        # TODO: Show user flash message about the changes being saved or error
        return toolkit.redirect_to(
            u'dataontosearch_tagger.edit',
            dataset_id=dataset_dict[u'id']
        )

    # Okay, create the form
    if not _get_can_edit(context, dataset_dict):
        return toolkit.abort(
            401,
            toolkit._(u'You are not allowed to edit concepts associated with '
                      u'this dataset')
        )

    # Fetch tags for the dataset
    existing_concepts = _get_existing_tags(context, dataset_dict)

    # Fetch available tags
    available_concepts = toolkit.get_action(u'dataontosearch_concept_list')(
        context,
        {}
    )

    # Fetch concepts that can be chosen
    available_concept_options = []
    for concept_iri, concept_info in available_concepts.iteritems():
        available_concept_options.append({
            u'value': concept_iri,
            u'text': concept_info[u'label'],
        })
    # Sort concepts by label
    available_concept_options.sort(key=lambda d: d[u'text'])
    # Add the default "empty" option
    available_concept_options.insert(0, {
        u'value': empty_value,
        u'text': toolkit._(u'-- No concept chosen --'),
    })

    return toolkit.render(
        u'dataontosearch_tagger_edit.html',
        {
            u'dataset': dataset_dict,
            u'concept_options': available_concept_options,
            u'default_option_value': empty_value,
            u'chosen_concepts': existing_concepts,
        }
    )
