.. You should enable this project on travis-ci.org and coveralls.io to make
   these badges work. The necessary Travis and Coverage config files have been
   generated for you.

.. image:: https://travis-ci.org/tobinus/ckanext-dataontosearch.svg?branch=master
    :target: https://travis-ci.org/tobinus/ckanext-dataontosearch

.. image:: https://coveralls.io/repos/tobinus/ckanext-dataontosearch/badge.svg
  :target: https://coveralls.io/r/tobinus/ckanext-dataontosearch

.. image:: https://pypip.in/download/ckanext-dataontosearch/badge.svg
    :target: https://pypi.python.org/pypi//ckanext-dataontosearch/
    :alt: Downloads

.. image:: https://pypip.in/version/ckanext-dataontosearch/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-dataontosearch/
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/ckanext-dataontosearch/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-dataontosearch/
    :alt: Supported Python versions

.. image:: https://pypip.in/status/ckanext-dataontosearch/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-dataontosearch/
    :alt: Development Status

.. image:: https://pypip.in/license/ckanext-dataontosearch/badge.svg
    :target: https://pypi.python.org/pypi/ckanext-dataontosearch/
    :alt: License

======================
ckanext-dataontosearch
======================

Extension for integrating CKAN with DataOntoSearch.

DataOntoSearch is a project which aims to make it easier to find datasets, by using a domain-specific ontology to find similar datasets. The software is run as a separate server, which other projects like CKAN can connect to.

There are two separate plugins provided with this extension. ``dataontosearch_tagging`` provides a way of associating datasets with concepts in the ontology. (Each such association is internally called a "tag", which should not be confused with the traditional tags CKAN provide.) ``dataontosearch_searching`` provides an integrated way of searching using DataOntoSearch.

The extension adds a link you can follow when editing datasets. From there, you can change what concepts are connected to what datasets.

The extension also adds a link to the alternative search method. Following it lets you search using DataOntoSearch.


------------
Requirements
------------

This plugin was developed for CKAN version 2.8. We have not checked what other versions it works with.


------------
Installation
------------

.. Add any additional install steps to the list below.
   For example installing any non-Python dependencies or adding any required
   config settings.

To install ckanext-dataontosearch:

1. Ensure that the ckanext-dcat_ extension is installed.

.. _ckanext-dcat: https://github.com/ckan/ckanext-dcat

2. Ensure that CKAN can accept multiple requests in parallel. For example, if
   you use ``gunicorn`` to run your application, you could use the ``-w`` flag
   to specify more than 1 worker: ``gunicorn -w 4 …`` (This is necessary
   because this extension's request to DataOntoSearch might cause
   DataOntoSearch to make a request back to CKAN, so the applications would end
   up waiting for each other in a deadlock.) Note that the ``debug`` setting
   must be set to ``false`` for CKAN to work in parallel.

3. Activate your CKAN virtual environment, for example::

     . /usr/lib/ckan/default/bin/activate

4. Install the ckanext-dataontosearch Python package into your virtual environment::

     pip install ckanext-dataontosearch

5. Add ``dataontosearch_tagging`` and ``dataontosearch_searching`` to the ``ckan.plugins`` setting in your CKAN
   config file (by default the config file is located at
   ``/etc/ckan/default/production.ini``). Both are not required, any one of them can be used alone, but that is rather uncommon. They need to be listed after the ``dcat`` plugins.

6. Add required settings::

     # Base URL where dataset_tagger is running
     ckan.dataontosearch.tagger_url = https://example.com/tagger

     # Base URL where the search for DataOntoSearch is running
     ckan.dataontosearch.search_url = https://example.com/search

     # The DataOntoSearch Configuration to use
     ckan.dataontosearch.configuration = 5c7ea259c556bb42803fa17e

7. Restart CKAN. For example if you've deployed CKAN with Apache on Ubuntu::

     sudo service apache2 reload


---------------
Config Settings
---------------

The required settings are described in the installation guide. In addition to those, you may specify the login used when connecting to DataOntoSearch::

    # Username and password to use when querying and tagging datasets in
    # DataOntoSearch (HTTP Basic Authentication)
    # (optional, default: no credentials).
    ckanext.dataontosearch.username = aladdin
    ckanext.dataontosearch.password = opensesame


In addition, you can also tell the extension to use the autotagged similarity graph when searching, instead of the manual tags::

    # Whether to use the autotagged graph instead of the manual one when
    # searching (optional, default: no).
    ckan.dataontosearch.use_autotag = yes


------------------------
Development Installation
------------------------

To install ckanext-dataontosearch for development, activate your CKAN virtualenv and
do::

    git clone https://github.com/tobinus/ckanext-dataontosearch.git
    cd ckanext-dataontosearch
    python setup.py develop
    pip install -r dev-requirements.txt


-----------------
Running the Tests
-----------------

To run the tests, do::

    nosetests --nologcapture --with-pylons=test.ini

To run the tests and produce a coverage report, first make sure you have
coverage installed in your virtualenv (``pip install coverage``) then run::

    nosetests --nologcapture --with-pylons=test.ini --with-coverage --cover-package=ckanext.dataontosearch --cover-inclusive --cover-erase --cover-tests


-------------------------------------------------
Releasing a New Version of ckanext-dataontosearch
-------------------------------------------------

ckanext-dataontosearch is availabe on PyPI as https://pypi.python.org/pypi/ckanext-dataontosearch.
To publish a new version to PyPI follow these steps:

1. Update the version number in the ``setup.py`` file.
   See `PEP 440 <http://legacy.python.org/dev/peps/pep-0440/#public-version-identifiers>`_
   for how to choose version numbers, using the principles of `semantic versioning <https://semver.org/>`_.

2. Create a source distribution of the new version::

     python setup.py sdist

3. Upload the source distribution to PyPI (assuming you have run ``pip install twine`` before)::

     twine upload dist/*

4. Tag the new release of the project on GitHub with the version number from
   the ``setup.py`` file. For example if the version number in ``setup.py`` is
   0.0.2 then do::

       git tag 0.0.2
       git push --tags
