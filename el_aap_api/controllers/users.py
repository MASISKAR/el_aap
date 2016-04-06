__author__ = 'schlitzer'
from bottle import request, response
import jsonschema
import jsonschema.exceptions

from el_aap_api.app import app
from el_aap_api.schemas import *


@app.get('/elaap/api/v1/users/_search')
def search(m_aa, m_users):
    m_aa.require_admin()
    return m_users.search(
            _ids=request.query.get('_id', None),
            admin=request.query.get('admin', None),
            fields=request.query.get('f', None)
    )


@app.get('/elaap/api/v1/users/<user>')
def get(m_aa, m_users, user):
    if user == '_self':
        user = m_aa.get_user()
    else:
        m_aa.require_admin()
    return m_users.get(user, request.query.get('f', None))


@app.put('/elaap/api/v1/users/<user>')
def update(m_aa, m_users, user):
    payload = request.json
    if user == '_self':
        user = m_aa.get_user()
        payload.pop('admin', None)
    else:
        m_aa.require_admin()
    jsonschema.validate(request.json, USERS_UPDATE, format_checker=jsonschema.draft4_format_checker)
    return m_users.update(user, payload)


@app.delete('/elaap/api/v1/users/<user>')
def delete(m_aa, m_users, m_roles, user):
    if user == '_self':
        user = m_aa.get_user()
    else:
        m_aa.require_admin()
    m_roles.remove_user_from_all(user)
    return m_users.delete(user)


@app.post('/elaap/api/v1/users')
def create(m_aa, m_users):
    m_aa.require_admin()
    jsonschema.validate(request.json, USERS_CREATE, format_checker=jsonschema.draft4_format_checker)
    result = m_users.create(request.json)
    response.status = 201
    return result
