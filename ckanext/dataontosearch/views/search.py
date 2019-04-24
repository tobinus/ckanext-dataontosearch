# encoding: utf-8
import logging

from flask import Blueprint

search = Blueprint(
    u'dataontosearch_search',
    __name__,
    url_prefix=u'/dataontosearch/search'
)

# TODO: Add route for performing and showing search queries
