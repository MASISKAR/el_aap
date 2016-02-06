Introduction
************
This project implements an ElasticSearch Authentication and Authorization reverse proxy,
that can be simply put in front of any ElasticSearch installation, without installing any
plugin into ElasticSearch.

IT consits of 4 main components:

 - the elasticsearch server that we like to secure:
 - el_aap: the proxy that will sit in front of elasticsearch
 - el_aap_api: the rest api to manage users, roles and permissions
 - mongodb to store all user, role and permission related stuff

The project is in a very early stage.

But the proxy is fully working.

TODO:
 - write tests
 - write documentation
 - create a frontend that is not swagger
 - create pypi package


The code has been developed on python3.4

Documentation
-------------

REST API documentation of the api part can be discovered at:

http://$HOST:$PORT/elaap/static/swagger/index.html#/

To use the api you have to login as a user that has an "admin" flag set to true, like the "default_admin"

Requirements
============
 - Running MongoDB
 - Running Elasticsearch
 - Python 3.x

Basic Installation
==================

Install dependencies:

  pip install bottle cachetools jsonscheme pep3143daemon pymongo requests waitress wsgi-request-logger


Clone the repository:

  git clone https://github.com/schlitzered/el_aap.git

Configuration
=============

el_aap, and el_aap_api are both expecting there configuration in /etc/el_aap/.

You can find example configuration files in the contrib folder.

The only things that need to be adjusted are the IP and port configurations of MongoDB and Elasticsearch. Everything else should stay unchanged. The other MongoDB sections have to be the same for both configuration files, except for the session part, that is not needed for el_aap proxy.

Running
"""""""
Both executeables can be found in the contrib folder. The Proxy is called el_aap, and the api/configuration interface is called el_aap_api.

Help can be discovered thru calling contrib/el_aap(_api) --help

Both can be started with:

  contrib/el_aap(_api) start

Both can be stopped with:

  contrib/el_aap(_api) quit

Running them in developement mode:

  contrib/el_aap(_api) devel

In developement mode, both will not daemonize and write errors and access logs to stdout.

Preparation
===========

execute:

  contrib/el_aap_api indicies

  contrib/el_aap_api create_admin

This will create some indices in MongoDB and a default admin user, that can be used to create other users, roles and permission rules.

The default admin is "default_admin" with the password "password"


Author
------

Stephan Schultchen <stephan.schultchen@gmail.com>

License
-------

Unless stated otherwise on-file el_app uses the MIT license,
check LICENSE file.

Contributing
------------

If you'd like to contribute, fork the project, make a patch and send a pull
request