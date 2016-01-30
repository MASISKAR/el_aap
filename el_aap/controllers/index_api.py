__author__ = 'schlitzer'

from bottle import request, response
import requests

from el_aap.app import app, str_index, endpoint
from el_aap_api.errors import *


@app.put('/_template')
@app.put('/_warmer')
def admin_put(m_aa):
    try:
        m_aa.require_permission(':', '')
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    r = requests.put(
            url=endpoint.endpoint+request.path,
            params=request.query,
            data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.put(str_index+'/_warmer')
@app.put(str_index+'/<_type>/_warmer')
@app.put(str_index)
@app.put(str_index+'/')
@app.put(str_index+'/_mapping/<_type>')
@app.put(str_index+'/_settings')
def put(m_aa, _index, _type=None):
    try:
        m_aa.require_permission(':index:manage:', _index)
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    r = requests.put(
            url=endpoint.endpoint+request.path,
            params=request.query,
            data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.post('/_flush')
@app.post('/_forcemerge')
@app.post('/_optimize')
@app.post('/_refresh')
@app.post('/_cache/clear')
def post(m_aa,):
    try:
        m_aa.require_permission(':', '')
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    r = requests.post(
            url=endpoint.endpoint+request.path,
            params=request.query,
            data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.post(str_index+'')
@app.post(str_index+'/')
@app.post(str_index+'/_cache/clear')
@app.post(str_index+'/_flush')
@app.post(str_index+'/_refresh')
@app.post(str_index+'/_optimize')
@app.post(str_index+'/_upgrade')
@app.post(str_index+'/_close')
@app.post(str_index+'/_open')
@app.post(str_index+'/_forcemerge')
def post(m_aa, _index):
    try:
        m_aa.require_permission(':index:manage:', _index)
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    r = requests.post(
        url=endpoint.endpoint+request.path,
        params=request.query,
        data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.delete(str_index+'')
@app.delete(str_index+'/')
def delete(m_aa, _index):
    try:
        for index in _index.split(','):
            m_aa.require_permission(':index:manage:', index)
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    r = requests.delete(
        url=endpoint.endpoint+request.path,
        params=request.query,
        data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.get('/_analyze')
@app.get('/_mapping')
@app.get('/_segments')
@app.get('/_recovery')
@app.get('/_shard_stores')
@app.get('/_stats')
@app.get('/_stats/')
@app.get('/_stats/<dummy_path>')
@app.get('/_template/<dummy>')
@app.get('/_all/_mapping')
@app.get('/_all/_settings')
@app.get('/_all/_settings/<dummy:path')
def admin_info(m_aa, dummy=None):
    try:
        m_aa.require_permission(':', '')
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    r = requests.get(
        url=endpoint.endpoint+request.path,
        params=request.query,
        data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.get(str_index+'/_analyze')
@app.get(str_index+'/_segments')
@app.get(str_index+'/_recovery')
@app.get(str_index+'/_shard_stores')
@app.get(str_index+'')
@app.get(str_index+'/')
@app.get(str_index+'/_stats')
@app.get(str_index+'/_stats/')
@app.get(str_index+'/_stats/<dummy:path>')
@app.get(str_index+'/_mapping')
@app.get(str_index+'/_mapping/')
@app.get(str_index+'/<dummy:re:^((_settings|_mappings|_warmers|_aliases)(,)?){1,}$>')
@app.get(str_index+'/_settings')
@app.get(str_index+'/_settings/<dummy:path')
@app.get(str_index+'/(<_type>)')
def info(m_aa, _index, dummy=None):
    try:
        for index in _index.split(','):
            m_aa.require_permission(':index:manage:monitor', index)
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    r = requests.get(
        url=endpoint.endpoint+request.path,
        params=request.query,
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


