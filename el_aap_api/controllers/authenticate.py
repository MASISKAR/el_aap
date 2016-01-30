__author__ = 'schlitzer'
from bottle import request, response

from el_aap_api.errors import BaseError
from el_aap_api.app import app


@app.post('/elaap/api/v1/authenticate')
def create(m_users, m_sessions):
    try:
        user = m_users.check_credentials(request.json)
        result = m_sessions.create(user)
        response.status = 201
        response.set_cookie('sid', result['_id'])
        response.set_cookie('token', result['token'])
        return result
    except BaseError as err:
        response.status = err.status
        return err.errmsg


@app.delete('/elaap/api/v1/authenticate')
def delete(m_sessions):
    try:
        token = m_sessions.get_token(request)
        response.delete_cookie('_id')
        response.delete_cookie('token')
        return m_sessions.delete(token['_id'])
    except BaseError as err:
        response.status = err.status
        return err.errmsg


@app.get('/elaap/api/v1/authenticate')
def verify(m_sessions):
    try:
        user = m_sessions.get_user(request)
        return user
    except BaseError as err:
        response.status = err.status
        return err.errmsg
