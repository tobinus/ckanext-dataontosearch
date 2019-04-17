import ckan.plugins.toolkit as toolkit


def dataontosearch_concept_list_auth(context, data_dict):
    # Simply require users to be logged in
    return {
        'success': True
    }


def dataontosearch_tagging_list_all_auth(context, data_dict):
    # Simply require users to be logged in
    return {
        'success': True
    }


def dataontosearch_tagging_list_auth(context, data_dict):
    # Simply require users to be logged in
    return {
        'success': True
    }


def dataontosearch_tagging_create_auth(context, data_dict):
    dataset_id_or_name = toolkit.get_or_bust(data_dict, 'dataset')
    try:
        toolkit.check_access('package_update', None, {'id': dataset_id_or_name})
        # User can edit the dataset, so let them edit the taggings
        return {
            'success': True
        }
    except toolkit.NotAuthorized as e:
        # Check failed for package_update
        return {
            'success': False,
            'msg': str(e)
        }


def dataontosearch_tagging_delete_auth(context, data_dict):
    # Use same permissions as for creating the tagging
    return dataontosearch_tagging_create_auth(context, data_dict)


def dataontosearch_dataset_delete_auth(context, data_dict):
    # This is not as destructive as deleting a dataset, so use same permissions
    # as for removing taggings individually.
    dataset_id_or_name = toolkit.get_or_bust(data_dict, 'id')
    tagging_permission = dataontosearch_tagging_delete_auth(
        context,
        {'dataset': dataset_id_or_name}
    )
    if not tagging_permission['success']:
        # Since this action is set to be triggered when a dataset is removed, we
        # must ensure that we are no stricter than the permissions for removing
        # a dataset. Normally this should not be a problem, but CKAN may have
        # been configured so permissions for removing datasets are relaxed.
        try:
            toolkit.check_access(
                'package_delete',
                None,
                {'id': dataset_id_or_name}
            )
            # Ok, user has permission to delete the dataset
            return {'success': True}
        except toolkit.NotAuthorized:
            # We can finally conclude that the user is not authorized to do this
            return tagging_permission
