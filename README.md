Introduction
------------
This project implements an ElasticSearch Authentication and Authorization reverse proxy,
that can be put in front of any ElasticSearch installation, without the need to install a
plugin into ElasticSearch. Authentication is done vie HTTP Basic AUTH.

IT consists of 5 main components:

 - the elasticsearch server that we like to secure:
 - el_aap: the reverse proxy that will secure our elasticsearch instance
 - el_aap_api: the rest api to manage users, roles and permissions
 - el_aap_cli: a command line tool, to manage users, roles and permission rules
 - mongodb to store all user, role and permission related stuff

The project is in a very early stage, but all features have been tested and seem to work as expected.

TODO:
 - write tests

The code has been developed  and tested on python3.4

API Documentation
-----------------

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
> pip install el-aap

Configuration
=============

el_aap, and el_aap_api are both expecting there configuration in /etc/el_aap/.

Example configuration for /etc/el_aap/el_aap.ini

```
[main]
dlog = el_aap.dlog
port = 9201

# Elasticsearch endpoint we like to secure.
[elasticsearch]
host = 127.0.0.1
port = 9200
scheme = http

[file:logging]
acc_log = el_aap_access.log
acc_retention = 7
app_log = el_aap_error.log
app_retention = 7
app_loglevel = DEBUG

# "main" MongoDB connection pool
[main:mongopool]
hosts = mongodb://localhost:27017,localhost:27018
db = el_aap
# pass =
# user =

# the permissions collection should use the "main" MongoDB pool, and the collection name "permission"
[permissions:mongocoll]
coll = permissions
pool = main

# the roles collection should use the "main" MongoDB pool, and the collection name "roles"
[roles:mongocoll]
coll = roles
pool = main

# the users collection should use the "main" MongoDB pool, and the collection name "users"
[users:mongocoll]
coll = users
pool = main
```

Example configuration for /etc/el_aap/el_aap_api.ini

```
[main]
dlog = el_aap_api_.dlog
# if not set, static file delivery is disabled
static_path = /path/to/static
port = 9000

# if this section is configured, password recovery feature via email is enabled
# [pw_recovery]
# api_url = http://el_aap_api.example.com
# www_url = http://el_aap_www.example.com/reset_password/
# from = elaap-pwrecovery@example.com
# subject = pw_recovery@example.com
# text_tmpl = /path/to/email/template/text_templ.jinja2
# html_tmpl = /path/to/email/template/html_templ.jinja2
# smtp_host = 127.0.0.1
# smtp_port = 10025

[file:logging]
acc_log = el_aap_api_access.log
acc_retention = 7
app_log = el_aap_api_error.log
app_retention = 7
app_loglevel = DEBUG

# "main" MongoDB connection pool
[main:mongopool]
hosts = mongodb://localhost:27017,localhost:27018
db = el_aap
# pass =
# user =

# the permissions collection should use the "main" MongoDB pool, and the collection name "permission"
[permissions:mongocoll]
coll = permissions
pool = main

# the roles collection should use the "main" MongoDB pool, and the collection name "roles"
[roles:mongocoll]
coll = roles
pool = main

# the users collection should use the "main" MongoDB pool, and the collection name "users"
[users:mongocoll]
coll = users
pool = main

# the sessions collection should use the "main" MongoDB pool, and the collection name "sessions"
[sessions:mongocoll]
coll = sessions
pool = main
```

The only things that needs to be adjusted are the IP and port configurations of MongoDB and Elasticsearch. Everything else should stay unchanged. The MongoDB sections in el_aap.ini have to match there counterparts in el_aap_api.ini and vise versa, except for the session section, that is only needed in el_aap_api.ini

Pre Running
===========
We assume that you already have a running Elasticsearch and MongoDB, setting up these is out of scope, and described well enough in other places.

First Run
=========
Before the first run, you have to create a default user and all the required indexes, this is done via:

    el_aap_api indicies
    el_aap_api create_admin
  
  The first command will create all the required indexes, the second one will create a default user called "default_admin" with the password "password" that has the admin flag set to True.

Running
=======
Both executables can be found in the contrib folder. The Proxy is called el_aap, and the api/configuration interface is called el_aap_api.

Help can be discovered thru calling contrib/el_aap(_api) --help

Both can be started with:

    contrib/el_aap(_api) start

Both can be stopped with:
    
    contrib/el_aap(_api) quit

Running them in developement mode:

    contrib/el_aap(_api) devel

In developement mode, both will not daemonize and write errors and access logs to stdout. The default pidfile of both daemons is written to "/var/run/el_aap/el_aap_api.pid" or "/var/run/el_aap/el_aap.pid".
Make sure you have created the folder "/var/run/el_aap/" before you try to start the daemons.

Managing Users, Roles and Permissions
=====================================

To manage the proxy configuration via the REST API you need a user that has the admin flag set to "True", all other user will only be able to authenticate against the reverse proxy itself via HTTP Basic AUTH.

Per default, no roles, and no permission rules are defined, so basically all access to elasticsearch via the proxy is denied!

Also notice that all user, roles, and passwords are cached in the reverse proxy for 2 Minutes, so making changes to passwords, roles, and other may take up to 2 minutes to become visible!

Managing users, roles and permissions can either be done directly via the REST API, or vie the command line tool called el_aap_cli.

Here we describe the usage of the el_aap_cli. 

To use the el_aap_cli tool, you have to create a file with the following content:

~/.el_aap_cli.ini
```
[main]
endpoint = http://127.0.0.1:9000/
user = default_admin
pass = password
``` 

This file contains your username and password, make sure no one has access to this file. You should use the command line tool only from you local workstation, and a user where only you have access to! You have been warned!

The el_aap_cli help can be called via

```
el_aap_cli --help
ElasticSearch Authentication and Authorization command line utility


positional arguments:
  {permissions,roles,users}
                        commands
    permissions         manage permissions
    roles               manage roles
    users               manage users

optional arguments:
  -h, --help            show this help message and exit
```    

The Options are structured into sub commands, that all except --help to give future details.

Manage Users
------------
This will create a user called "adminuser" with the password "password", that has the admin flag set. this means that this admin can also manage other users, roles and permissions
```
el_aap_cli users add --id adminuser --admin --email admin_user@example.com --name "Administrative User" --password password
``` 

This will create a user called "test_user" with the password "password", without the admin flag set.
```
el_aap_cli users add --id test_user --email test_user@example.com --name "Test User" --password password
```

see the following command for a detailed list of available options.

    el_api_cli users --help
    el_api_cli users {subcommand} --help

Manage Roles
------------
This will create a new role called "testrole1" that has the admin_user and the default_admin as member.
```
el_aap_cli roles add --id testrole1 --description "test role 1" --users admin_user,default_admin
``` 

This will add the "test_user to the "testrole1".
```
el_aap_cli roles add_users --id testrole1 --users test_user
``` 

This will remove the "default_admin" from the test_role1.
```
el_aap_cli roles del_users --id testrole1 --users default_admin
``` 

see the following command for a detailed list of available options.

    el_api_cli roles --help
    el_api_cli roles {subcommand} --help
  
Manage Permissions
------------------
Permissions grand Roles access to Indexes, based and the given scope, where the scope is a regular expression that is matched against the index name, and the assigned permissions to the permission Rule.

Here is a list of all available permissions that can be used:

 - :
 - :cluster:
 - :cluster:monitor
 - :index:
 - :index:crud:
 - :index:crud:create
 - :index:crud:read
 - :index:crud:update
 - :index:crud:delete
 - :index:crud:search
 - :index:manage:
 - :index:manage:monitor

The :index:crud:* permissions grant access to CRUD related Index operations, including Searches. ":index:crud:" includes all CRUD and Search related operations

The :index:manage:monitor permissions can be used to execute index monitoring related tasks, like reading the list of aliases for an index. The :index:manage: permissions allows the creation of new index aliases and the like, it also includes the :index:manage:monitor privilege.

The :index: privilige contains the index CRUD and index manage privileges.

:cluster:monitor grants acces to cluster monitoring related endpoints.
:cluster: grants access to all cluster related tasks, including monitoring.

The : permissions grants access to all of the above permissions.

    el_api_cli permissions --help
    el_api_cli permissions {subcommand} --help



Creating a Permission Rule
--------------------------
Create a permission rule which grants read and search permissions to all indexes and index aliases that match apache-acces* to the role testrole1
```
el_aap_cli permissions add --id apache-access-read --description "Grant Read Permissions to the Apache Access Log Index" --scope 'apache-access*' --roles testrole1 --permissions :index:crud:read,:index:crud:search
``` 

Author
======

Stephan Schultchen <stephan.schultchen@gmail.com>

License
=======

Unless stated otherwise on-file el_app uses the MIT license,
check LICENSE file.

Contributing
============

If you'd like to contribute, fork the project, make a patch and send a pull
request