__author__ = 'schlitzer'

from bottle import request, response
import requests

from el_aap.app import app, endpoint


@app.get('/_plugin/<dummy:path>')
def plugin_get(m_aa, dummy=None):
    m_aa.require_permission(':', '')
    r = requests.get(
        allow_redirects=False,
        url=endpoint.endpoint+request.path,
        params=request.query,
        headers=request.headers,
        data=request.body
    )
    response.status = r.status_code
    for header, value in r.headers.items():
        if header == 'Content-Length':
            continue
        response.set_header(header, value)
    return r.content


@app.post('/_plugin/<dummy:path>')
def plugin_post(m_aa, dummy=None):
    m_aa.require_permission(':', '')
    r = requests.post(
        allow_redirects=False,
        url=endpoint.endpoint+request.path,
        params=request.query,
        headers=request.headers,
        data=request.body
    )
    response.status = r.status_code
    for header, value in r.headers.items():
        if header == 'Content-Length':
            continue
        response.set_header(header, value)
    return r.content


@app.put('/_plugin/<dummy:path>')
def plugin_put(m_aa, dummy=None):
    m_aa.require_permission(':', '')
    r = requests.put(
        allow_redirects=False,
        url=endpoint.endpoint+request.path,
        params=request.query,
        headers=request.headers,
        data=request.body
    )
    response.status = r.status_code
    for header, value in r.headers.items():
        if header == 'Content-Length':
            continue
        response.set_header(header, value)
    return r.content


@app.delete('/_plugin/<dummy:path>')
def plugin_get(m_aa, dummy=None):
    m_aa.require_permission(':', '')
    r = requests.delete(
        allow_redirects=False,
        url=endpoint.endpoint+request.path,
        params=request.query,
        headers=request.headers,
        data=request.body
    )
    response.status = r.status_code
    for header, value in r.headers.items():
        if header == 'Content-Length':
            continue
        response.set_header(header, value)
    return r.content

