__author__ = 'schlitzer'
from bottle import request, response
import jsonschema
import jsonschema.exceptions

from el_aap_api.app import app
from el_aap_api.errors import InvalidBody
from el_aap_api.schemas import *


@app.get('/elaap/api/v1/roles/_search')
def search(m_roles, m_sessions, m_users):
    m_users.require_admin(m_sessions.get_user(request))
    result = m_roles.search(
            _ids=request.query.get('_id', None),
            users=request.query.get('users', None),
            fields=request.query.get('f', None)
    )
    return result


@app.get('/elaap/api/v1/roles/<role>')
def get(m_roles, m_sessions, m_users, role):
    m_users.require_admin(m_sessions.get_user(request))
    result = m_roles.get(role, request.query.get('f', None))
    return result


@app.post('/elaap/api/v1/roles')
def create(m_roles, m_sessions, m_users):
    jsonschema.validate(request.json, ROLES_CREATE, format_checker=jsonschema.draft4_format_checker)
    m_users.require_admin(m_sessions.get_user(request))
    if 'users' in request.json:
        if not m_users.check_ids(request.json['users']):
            raise InvalidBody("non existing users selected")
    result = m_roles.create(request.json)
    response.status = 201
    return result


@app.put('/elaap/api/v1/roles/<role>')
def update(m_roles, m_sessions, m_users, role):
    jsonschema.validate(request.json, ROLES_UPDATE, format_checker=jsonschema.draft4_format_checker)
    m_users.require_admin(m_sessions.get_user(request))
    if 'users' in request.json:
        if not m_users.check_ids(request.json['users']):
            raise InvalidBody("non existing users selected")
    return m_roles.update(role, request.json)


@app.put('/elaap/api/v1/roles/<role>/users')
def update_users(m_roles, m_sessions, m_users, role):
    m_users.require_admin(m_sessions.get_user(request))
    if type(request.json) == list:
        if not m_users.check_ids(request.json):
            raise InvalidBody("non existing users selected")
    else:
        raise InvalidBody("must be of type list")
    return m_roles.add_users(role, request.json)


@app.delete('/elaap/api/v1/roles/<role>')
def delete(m_roles, m_sessions, m_users, m_permissions, role):
    m_users.require_admin(m_sessions.get_user(request))
    m_permissions.remove_role_from_all(role)
    return m_roles.delete(role)


@app.delete('/elaap/api/v1/roles/<role>/users')
def update_users(m_roles, m_sessions, m_users, role):
    m_users.require_admin(m_sessions.get_user(request))
    if not type(request.json) == list:
        raise InvalidBody("must be of type list")
    return m_roles.remove_users(role, request.json)
