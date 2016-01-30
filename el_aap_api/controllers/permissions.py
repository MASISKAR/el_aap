__author__ = 'schlitzer'
from bottle import request, response

from el_aap_api.errors import BaseError
from el_aap_api.app import app


@app.get('/elaap/api/v1/permissions/_search')
def search(m_permissions, m_sessions, m_users):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        result = m_permissions.search(
            _id=request.query.get('_id', None),
            permissions=request.query.get('permissions', None),
            scope=request.query.get('scope', None),
            roles=request.query.get('roles', None),
            fields=request.query.get('f', None)
        )
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    return result


@app.post('/elaap/api/v1/permissions')
def create(m_permissions, m_sessions, m_users, m_roles):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        result = m_permissions.create(request.json, m_roles.check_ids)
        response.status = 201
        return result
    except BaseError as err:
        response.status = err.status
        return err.errmsg


@app.get('/elaap/api/v1/permissions/<permission>')
def get(m_permissions, m_sessions, m_users, permission):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        result = m_permissions.get(permission, request.query.get('f', None))
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    return result


@app.put('/elaap/api/v1/permissions/<permission>')
def update(m_permissions, m_sessions, m_users, m_roles, permission):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        return m_permissions.update(permission, request.json, m_roles.check_ids)
    except BaseError as err:
        response.status = err.status
        return err.errmsg


@app.delete('/elaap/api/v1/permissions/<permission>')
def delete(m_permissions, m_sessions, m_users, permission):
    try:
        m_users.require_admin(m_sessions.get_user(request))
        return m_permissions.delete(permission)
    except BaseError as err:
        response.status = err.status
        return err.errmsg
