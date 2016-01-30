Introduction
************
This project implements an ElasticSearch Authentication and Authorization reverse proxy,
that can be simply put in front of any ElasticSearch installation, without installing any
plugin into ElasticSearch.

The whole thing consists of 4 main components:

1: the elasticsearch server that we like to secure:
2: el_aap: the proxy that will sit in front of elasticsearch
3: el_aap_api: the rest api to manage users, roles and permissions
4: mongodb to store all user, role and permission related stuff

The project is in a very early stage.

But the proxy is fully working.

TODO:
write tests
write documentation
create a frontend that is not swagger


The code has been developed on python3.4

Documentation
-------------

REST API documentation of the api part can be discovered at:

http://$HOST:$PORT/elaap/static/swagger/index.html#/

Installing
----------

This project uses the following external libs:

bottle
cachetools
pep3143daemon
pymongo
requests
validation
waitress
wsgi-request-logger


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
request.