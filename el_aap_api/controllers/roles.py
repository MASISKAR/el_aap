__author__ = 'schlitzer'
from bottle import request, response

from el_aap_api.errors import BaseError
from el_aap_api.app import app


@app.get('/elaap/api/v1/roles/_search')
def search(m_roles, m_sessions, m_users):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        result = m_roles.search(
                _id=request.query.get('_id', None),
                users=request.query.get('users', None),
                fields=request.query.get('f', None)
        )
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    return result


@app.get('/elaap/api/v1/roles/<role>')
def get(m_roles, m_sessions, m_users, role):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        result = m_roles.get(role, request.query.get('f', None))
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    return result


@app.post('/elaap/api/v1/roles')
def create(m_roles, m_sessions, m_users):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        result = m_roles.create(request.json, m_users.check_ids)
        response.status = 201
        return result
    except BaseError as err:
        response.status = err.status
        return err.errmsg


@app.put('/elaap/api/v1/roles/<role>')
def update(m_roles, m_sessions, m_users, role):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        return m_roles.update(role, request.json, m_users.check_ids)
    except BaseError as err:
        response.status = err.status
        return err.errmsg


@app.delete('/elaap/api/v1/roles/<role>')
def delete(m_roles, m_sessions, m_users, role):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        return m_roles.delete(role)
    except BaseError as err:
        response.status = err.status
        return err.errmsg
