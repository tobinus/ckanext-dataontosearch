# encoding: utf-8
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


class TestUrlForPlugin(plugins.SingletonPlugin):
    """
    Plugin for testing out the toolkit.url_for function.
    """

    plugins.implements(plugins.IActions)

    # IActions

    def get_actions(self):
        return {
            u'test_url_for': test_url_for,
        }


@toolkit.side_effect_free
def test_url_for(context, data_dict):
    # url_for fails when it creates unicode and not str, so it must be fed str
    endpoint = data_dict.pop(u'endpoint', u'dataset.read').encode(u'utf8')
    extra_args = {key: value.encode(u'utf8') for key, value in data_dict.iteritems()}
    return toolkit.url_for(
        endpoint,
        **extra_args
    )
