__author__ = 'schlitzer'
from bottle import request, response
import jsonschema
import jsonschema.exceptions

from el_aap_api.app import app
from el_aap_api.errors import InvalidBody
from el_aap_api.schemas import *


@app.get('/elaap/api/v1/permissions/_search')
def search(m_permissions, m_sessions, m_users):
    m_users.require_admin(m_sessions.get_user(request))
    return m_permissions.search(
        _ids=request.query.get('_id', None),
        permissions=request.query.get('permissions', None),
        scope=request.query.get('scope', None),
        roles=request.query.get('roles', None),
        fields=request.query.get('f', None)
    )


@app.post('/elaap/api/v1/permissions')
def create(m_permissions, m_sessions, m_users, m_roles):
    jsonschema.validate(request.json, PERMISSIONS_CREATE, format_checker=jsonschema.draft4_format_checker)
    if 'roles' in request.json:
        if not m_roles.check_ids(request.json['roles']):
            raise InvalidBody('some roles missing')
    m_users.require_admin(m_sessions.get_user(request))
    result = m_permissions.create(request.json)
    response.status = 201
    return result


@app.get('/elaap/api/v1/permissions/<permission>')
def get(m_permissions, m_sessions, m_users, permission):
    m_users.require_admin(m_sessions.get_user(request))
    return m_permissions.get(permission, request.query.get('f', None))


@app.put('/elaap/api/v1/permissions/<permission>')
def update(m_permissions, m_sessions, m_users, m_roles, permission):
    jsonschema.validate(request.json, PERMISSIONS_UPDATE, format_checker=jsonschema.draft4_format_checker)
    if 'roles' in request.json:
        if not m_roles.check_ids(request.json['roles']):
            raise InvalidBody('some roles missing')
    m_users.require_admin(m_sessions.get_user(request))
    return m_permissions.update(permission, request.json)


@app.delete('/elaap/api/v1/permissions/<permission>')
def delete(m_permissions, m_sessions, m_users, permission):
    m_users.require_admin(m_sessions.get_user(request))
    return m_permissions.delete(permission)
