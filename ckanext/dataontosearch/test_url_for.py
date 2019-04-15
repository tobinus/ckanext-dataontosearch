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
            'test_url_for': test_url_for,
        }


@toolkit.side_effect_free
def test_url_for(context, data_dict):
    endpoint = data_dict.pop('endpoint', 'dataset.read').encode('utf8')
    extra_args = {key: value.encode('utf8') for key, value in data_dict.iteritems()}
    return toolkit.url_for(
        endpoint,
        **extra_args
    )
