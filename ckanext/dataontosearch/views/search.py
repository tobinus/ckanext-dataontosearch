# encoding: utf-8
import logging
import ckan.plugins.toolkit as toolkit

from flask import Blueprint, request

from ckanext.dataontosearch.views.utils import _log_exceptions

logger = logging.getLogger(__name__)

search = Blueprint(
    u'dataontosearch_search',
    __name__,
    url_prefix=u'/dataontosearch/search'
)


@search.route(u'')
@_log_exceptions
def do_search():
    context = {}

    query = request.args.get(u'q', u'').strip()

    if query:
        result = toolkit.get_action(u'dataontosearch_dataset_search')(
            context,
            {u'q': query}
        )
    else:
        result = None

    return toolkit.render(
        u'dataontosearch_search.html',
        {
            u'search': result,
            u'query': query,
        }
    )
