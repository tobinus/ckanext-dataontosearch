# encoding: utf-8
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

import ckanext.dataontosearch.logic as logic
import ckanext.dataontosearch.auth as auth


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
            u'dataontosearch_concept_list': logic.dataontosearch_concept_list,
            u'dataontosearch_tag_list_all': logic.dataontosearch_tag_list_all,
            u'dataontosearch_tag_list': logic.dataontosearch_tag_list,
            u'dataontosearch_tag_create': logic.dataontosearch_tag_create,
            u'dataontosearch_tag_delete': logic.dataontosearch_tag_delete,
            u'dataontosearch_dataset_delete':
                logic.dataontosearch_dataset_delete,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            u'dataontosearch_concept_list': auth.dataontosearch_concept_list,
            u'dataontosearch_tag_list_all': auth.dataontosearch_tag_list_all,
            u'dataontosearch_tag_list': auth.dataontosearch_tag_list,
            u'dataontosearch_tag_create': auth.dataontosearch_tag_create,
            u'dataontosearch_tag_delete': auth.dataontosearch_tag_delete,
            u'dataontosearch_dataset_delete':
                auth.dataontosearch_dataset_delete,
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
    plugins.implements(plugins.IActions)
    plugins.implements(plugins.IAuthFunctions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, u'templates')
        toolkit.add_public_directory(config_, u'public')
        toolkit.add_resource(u'fanstatic', u'dataontosearch')

    # IActions

    def get_actions(self):
        return {
            u'dataontosearch_dataset_search':
                logic.dataontosearch_dataset_search,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            u'dataontosearch_dataset_search':
                auth.dataontosearch_dataset_search,
        }
