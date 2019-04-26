# encoding: utf-8
import ckan.plugins.toolkit as toolkit


@toolkit.auth_allow_anonymous_access
def dataontosearch_concept_list(context, data_dict):
    # Allow everyone
    return {
        u'success': True
    }


@toolkit.auth_allow_anonymous_access
def dataontosearch_tag_list_all(context, data_dict):
    # Allow everyone
    return {
        u'success': True
    }


@toolkit.auth_allow_anonymous_access
def dataontosearch_tag_list(context, data_dict):
    # Allow everyone
    return {
        u'success': True
    }


def dataontosearch_tag_create(context, data_dict):
    dataset_id_or_name = toolkit.get_or_bust(data_dict, u'dataset')
    try:
        toolkit.check_access(u'package_update', None, {u'id': dataset_id_or_name})
        # User can edit the dataset, so let them edit the taggings
        return {
            u'success': True
        }
    except toolkit.NotAuthorized as e:
        # Check failed for package_update
        return {
            u'success': False,
            u'msg': str(e)
        }


def dataontosearch_tag_delete(context, data_dict):
    # Use same permissions as for creating the tagging
    return dataontosearch_tag_create(context, data_dict)


def dataontosearch_dataset_delete(context, data_dict):
    # This is not as destructive as deleting a dataset, so use same permissions
    # as for removing taggings individually.
    dataset_id_or_name = toolkit.get_or_bust(data_dict, u'id')
    tagging_permission = dataontosearch_tag_delete(
        context,
        {u'dataset': dataset_id_or_name}
    )
    if not tagging_permission[u'success']:
        # Since this action is set to be triggered when a dataset is removed, we
        # must ensure that we are no stricter than the permissions for removing
        # a dataset. Normally this should not be a problem, but CKAN may have
        # been configured so permissions for removing datasets are relaxed.
        try:
            toolkit.check_access(
                u'package_delete',
                None,
                {u'id': dataset_id_or_name}
            )
            # Ok, user has permission to delete the dataset
            return {u'success': True}
        except toolkit.NotAuthorized:
            # We can finally conclude that the user is not authorized to do this
            return tagging_permission


@toolkit.auth_allow_anonymous_access
def dataontosearch_dataset_search(context, data_dict):
    # Let everyone enjoy the joy of searching
    return {
        u'success': True
    }
