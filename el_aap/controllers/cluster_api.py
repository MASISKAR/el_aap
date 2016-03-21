__author__ = 'schlitzer'

from bottle import request, response
import requests

from el_aap.app import app, endpoint


@app.get('/')
def slash(m_aa, dummy=None):
    m_aa.check_auth()
    r = requests.get(
        url=endpoint.endpoint+request.path,
        params=request.query,
        data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.get('/_cluster')
@app.get('/_cluster/')
@app.get('/_cluster/<dummy:path>')
@app.get('/_cluster/<dummy:path>/')
@app.get('/_nodes')
@app.get('/_nodes/')
@app.get('/_nodes/<dummy:path>')
@app.get('/_nodes/<dummy:path>/')
def info_get(m_aa, dummy=None):
    m_aa.require_permission(':cluster:monitor', '')
    r = requests.get(
            url=endpoint.endpoint+request.path,
            params=request.query,
            data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.post('/_cluster')
@app.post('/_cluster/')
@app.post('/_cluster/<dummy:path>')
@app.post('/_cluster/<dummy:path>/')
@app.post('/_nodes')
@app.post('/_nodes/')
@app.post('/_nodes/<dummy:path>')
@app.post('/_nodes/<dummy:path>/')
def info_post(m_aa, dummy=None):
    m_aa.require_permission(':cluster:', '')
    r = requests.post(
            url=endpoint.endpoint+request.path,
            params=request.query,
            data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()
