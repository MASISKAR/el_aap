__author__ = 'schlitzer'

import json

from bottle import request, response
import requests

from el_aap.app import app, str_index, str_id, endpoint
from el_aap_api.errors import *


@app.get(str_index+'/<_type>/'+str_id+'/count')
@app.get(str_index+'/<_type>/'+str_id+'/_explain')
@app.get(str_index+'/<_type>/'+str_id+'/_percolate')
def get(m_aa, _index, _type, _id):
    m_aa.require_permission(':index:crud:search', _index)
    r = requests.get(
            url=endpoint.endpoint+request.path,
            params=request.query,
            data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.get(str_index+'/_count')
@app.get(str_index+'/<_type>/_count')
@app.get(str_index+'/_field_stats')
@app.get(str_index+'/<_type>/_field_stats')
@app.get(str_index+'/_search')
@app.get(str_index+'/<_type>/_search')
@app.get(str_index+'/_search/exists')
@app.get(str_index+'/<_type>/_search/exists')
@app.get(str_index+'/_search_shards')
@app.get(str_index+'/<_type>/_search_shards')
@app.get(str_index+'/_validate/query')
@app.get(str_index+'/<_type>/_validate/query')
def search_get(m_aa, _index, _type=None):
    for index in _index.split(','):
        m_aa.require_permission(':index:crud:search', index)
    r = requests.get(
            url=endpoint.endpoint+request.path,
            params=request.query,
            data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.post(str_index+'/_count')
@app.post(str_index+'/<_type>/_count')
@app.post(str_index+'/_field_stats')
@app.post(str_index+'/<_type>/_field_stats')
@app.post(str_index+'/_search')
@app.post(str_index+'/<_type>/_search')
@app.post(str_index+'/_search/exists')
@app.post(str_index+'/<_type>/_search/exists')
@app.post(str_index+'/_search_shards')
@app.post(str_index+'/<_type>/_search_shards')
@app.post(str_index+'/_validate/query')
@app.post(str_index+'/<_type>/_validate/query')
def search_post(m_aa, _index, _type=None):
    for index in _index.split(','):
        m_aa.require_permission(':index:crud:search', index)
    r = requests.post(
        url=endpoint.endpoint+request.path,
        params=request.query,
        data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.get('/_count')
@app.get('/_field_stats')
@app.get('/_search')
@app.get('/_search/exists')
@app.get('/_validate/query')
def search_admin_get(m_aa):
    m_aa.require_permission(':', '')
    r = requests.get(
            url=endpoint.endpoint+request.path,
            params=request.query,
            data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.post('/_count')
@app.post('/_field_stats')
@app.post('/_search')
@app.post('/_search/exists')
@app.post('/_validate/query')
def search_admin_post(m_aa):
    m_aa.require_permission(':', '')
    r = requests.post(
            url=endpoint.endpoint+request.path,
            params=request.query,
            data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.get('/_msearch')
@app.get(str_index+'/_msearch')
@app.get(str_index+'/<_type>/_msearch')
def m_search(m_aa, _index=None, _type=None):
    if _index:
        for index in _index.split(','):
            m_aa.require_permission(':index:crud:search', index)
    header = True
    for data in request.body.readlines():
        if not header:
            header = True
            continue
        try:
            for index in json.loads(data.decode('utf8'))['index'].split(','):
                m_aa.require_permission(':index:crud:search', index)
        except (KeyError, ValueError):
            if not _index:
                raise PermError
        header = False
    request.body.seek(0)
    r = requests.get(
        url=endpoint.endpoint+request.path,
        params=request.query,
        data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.get('/_mpercolate')
@app.get(str_index+'/_mpercolate')
@app.get(str_index+'/<_type>/_mpercolate')
def m_search(m_aa, _index=None, _type=None):
    if _index:
        for index in _index.split(','):
            m_aa.require_permission(':index:crud:search', index)
    header = True
    for data in request.body.readlines():
        if not header:
            header = True
            continue
        try:
            for index in json.loads(data.decode('utf8'))['percolate']['index'].split(','):
                m_aa.require_permission(':index:crud:search', index)
        except (KeyError, ValueError):
            if not _index:
                raise PermError
        header = False
    request.body.seek(0)
    r = requests.get(
            url=endpoint.endpoint+request.path,
            params=request.query,
            data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


@app.post('/_field_stats')
def field_stats(m_aa):
    m_aa.require_permission(':', '')
    r = requests.post(
            url=endpoint.endpoint+request.path,
            params=request.query,
            data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()
