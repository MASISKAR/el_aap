__author__ = 'schlitzer'
from bottle import request, response
import jsonschema
import jsonschema.exceptions

from el_aap_api.app import app
from el_aap_api.schemas import *


@app.get('/elaap/api/v1/users/_search')
def search(m_users, m_sessions):
    m_users.require_admin(m_sessions.get_user(request))
    return m_users.search(
            _ids=request.query.get('_id', None),
            admin=request.query.get('admin', None),
            fields=request.query.get('f', None)
    )


@app.get('/elaap/api/v1/users/<user>')
def get(m_users, m_sessions, user):
    m_users.require_admin(m_sessions.get_user(request))
    return m_users.get(user, request.query.get('f', None))


@app.put('/elaap/api/v1/users/<user>')
def update(m_users, m_sessions, user):
    jsonschema.validate(request.json, USERS_UPDATE, format_checker=jsonschema.draft4_format_checker)
    m_users.require_admin(m_sessions.get_user(request))
    return m_users.update(user, request.json)


@app.delete('/elaap/api/v1/users/<user>')
def delete(m_users, m_sessions, m_roles, user):
    m_users.require_admin(m_sessions.get_user(request))
    m_roles.remove_user(user)
    return m_users.delete(user)


@app.post('/elaap/api/v1/users')
def create(m_users, m_sessions):
    jsonschema.validate(request.json, USERS_CREATE, format_checker=jsonschema.draft4_format_checker)
    m_users.require_admin(m_sessions.get_user(request))
    result = m_users.create(request.json)
    response.status = 201
    return result


@app.delete('/elaap/api/v1/users/_self')
def self_delete(m_users, m_sessions):
    return m_users.delete(m_sessions.get_user(request))


@app.get('/elaap/api/v1/users/_self')
def self_get(m_users, m_sessions):
    return m_users.get(
        m_sessions.get_user(request),
        request.query.get('f', None)
    )


@app.put('/elaap/api/v1/users/_self')
def self_update(m_users, m_sessions):
    payload = request.json
    user = m_sessions.get_user(request)
    if not m_users.is_admin(user):
        payload.pop('admin', None)
    return m_users.update(user, payload)
