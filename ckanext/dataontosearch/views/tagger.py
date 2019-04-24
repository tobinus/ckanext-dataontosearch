# encoding: utf-8
import logging

from flask import Blueprint

tagger = Blueprint(
    u'dataontosearch_tagger',
    __name__,
    url_prefix=u'/dataontosearch/tagger'
)

# TODO: Add routes for seeing and modifying tags
