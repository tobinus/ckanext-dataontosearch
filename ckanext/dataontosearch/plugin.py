# encoding: utf-8
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.dataontosearch.logic import (
    dataontosearch_concept_list, dataontosearch_tagging_list_all,
    dataontosearch_tagging_list, dataontosearch_tagging_create,
    dataontosearch_tagging_delete, dataontosearch_dataset_delete
)
from ckanext.dataontosearch.auth import (
    dataontosearch_concept_list_auth, dataontosearch_tagging_list_all_auth,
    dataontosearch_tagging_list_auth, dataontosearch_tagging_create_auth,
    dataontosearch_tagging_delete_auth, dataontosearch_dataset_delete_auth
)


# TODO: Check if "tagging" is correct noun to use, or should I use "tag"?


class DataOntoSearch_TaggingPlugin(
    plugins.SingletonPlugin
):
    """
    Plugin for tagging datasets with relevant concepts.
    """
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)
    plugins.implements(plugins.IPackageController, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, u'templates')
        toolkit.add_public_directory(config_, u'public')
        toolkit.add_resource(u'fanstatic', u'dataontosearch')

    # IActions

    def get_actions(self):
        return {
            u'dataontosearch_concept_list': dataontosearch_concept_list,
            u'dataontosearch_tagging_list_all': dataontosearch_tagging_list_all,
            u'dataontosearch_tagging_list': dataontosearch_tagging_list,
            u'dataontosearch_tagging_create': dataontosearch_tagging_create,
            u'dataontosearch_tagging_delete': dataontosearch_tagging_delete,
            u'dataontosearch_dataset_delete': dataontosearch_dataset_delete,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            u'dataontosearch_concept_list': dataontosearch_concept_list_auth,
            u'dataontosearch_tagging_list_all': dataontosearch_tagging_list_all_auth,
            u'dataontosearch_tagging_list': dataontosearch_tagging_list_auth,
            u'dataontosearch_tagging_create': dataontosearch_tagging_create_auth,
            u'dataontosearch_tagging_delete': dataontosearch_tagging_delete_auth,
            u'dataontosearch_dataset_delete': dataontosearch_dataset_delete_auth,
        }

    # IPackageController

    def delete(self, entity):
        # Delete dataset from DataOntoSearch when it is deleted from CKAN
        toolkit.get_action(u'dataontosearch_dataset_delete')(None, {
            u'id': entity.id
        })


class DataOntoSearch_SearchingPlugin(plugins.SingletonPlugin):
    """
    Plugin for searching for datasets using semantic search in DataOntoSearch.
    """
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, u'templates')
        toolkit.add_public_directory(config_, u'public')
        toolkit.add_resource(u'fanstatic', u'dataontosearch')
