__author__ = 'schlitzer'
from bottle import request, response

from el_aap_api.errors import BaseError
from el_aap_api.app import app


@app.get('/elaap/api/v1/users/_search')
def search(m_users, m_sessions):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        result = m_users.search(
                _ids=request.query.get('_id', None),
                admin=request.query.get('admin', None),
                fields=request.query.get('f', None)
        )
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    return result


@app.get('/elaap/api/v1/users/<user>')
def get(m_users, m_sessions, user):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        result = m_users.get(user, request.query.get('f', None))
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    return result


@app.put('/elaap/api/v1/users/<user>')
def update(m_users, m_sessions, user):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        return m_users.update(user, request.json)
    except BaseError as err:
        response.status = err.status
        return err.errmsg


@app.delete('/elaap/api/v1/users/<user>')
def delete(m_users, m_sessions, user):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        return m_users.delete(user)
    except BaseError as err:
        response.status = err.status
        return err.errmsg


@app.post('/elaap/api/v1/users')
def create(m_users, m_sessions):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        result = m_users.create(request.json)
        response.status = 201
        return result
    except BaseError as err:
        response.status = err.status
        return err.errmsg


@app.delete('/elaap/api/v1/users/_self')
def self_delete(m_users, m_sessions):
    try:
        return m_users.delete(m_sessions.get_user(request))
    except BaseError as err:
        response.status = err.status
        return err.errmsg


@app.get('/elaap/api/v1/users/_self')
def self_get(m_users, m_sessions):
    try:
        result = m_users.get(
            m_sessions.get_user(request),
            request.query.get('f', None)
        )
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    return result


@app.put('/elaap/api/v1/users/_self')
def self_update(m_users, m_sessions):
    try:
        payload = request.json
        user = m_sessions.get_user(request)
        if not m_users.is_admin(user):
            payload.pop('admin', None)
        return m_users.update(user, payload)
    except BaseError as err:
        response.status = err.status
        return err.errmsg
