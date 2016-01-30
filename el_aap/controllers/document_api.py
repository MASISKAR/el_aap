__author__ = 'schlitzer'

import json

from bottle import request, response
import requests

from el_aap.app import app, app_logger, str_id, str_index, endpoint
from el_aap_api.errors import *

# bulk api
@app.post('/_bulk')
@app.post(str_index+'/_bulk')
@app.post(str_index+'/<_type>/_bulk')
def bulk(m_aa, _index=None, _type=None):
    if _index:
        try:
            m_aa.require_permission(':index:crud:read', _index)
        except BaseError as err:
            response.status = err.status
            return err.errmsg
    for data in request.body.readlines():
        data = json.loads(data.decode('utf8'))
        try:
            index = data['index']['_index']
            m_aa.require_permission(':index:crud:read', index)
        except KeyError:
            continue
        except BaseError as err:
            response.status = err.status
            return err.errmsg
    request.body.seek(0)
    r = requests.post(
            url=endpoint.endpoint+request.path,
            params=request.query,
            data=request.body
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


# Index document without explicit _id
@app.post(str_index+'/<_type>/')
def create(m_aa, _index, _type):
    try:
        m_aa.require_permission(':index:crud:create', _index)
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


# mget & mtermvectors api´s
@app.get('/_mget')
@app.get(str_index+'/_mget')
@app.get(str_index+'/<_type>/_mget')
@app.get('/_mtermvectors')
@app.get(str_index+'/_mtermvectors')
@app.get(str_index+'/<_type>/_mtermvectors')
def mget_mtermvectors(m_aa, _index=None, _type=None):
    if _index:
        try:
            m_aa.require_permission(':index:crud:read', _index)
        except BaseError as err:
            response.status = err.status
            return err.errmsg
    data = list()
    for line in request.body.readlines():
        data.append(line.decode('utf8'))
    data = json.loads(''.join(data))
    request.body.seek(0)
    if 'docs' in data:
        for doc in data['docs']:
            try:
                if '_index' in doc:
                    m_aa.require_permission(':index:crud:read', doc['_index'])
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


# termvectors
@app.get(str_index+'/<_type>/_termvectors')
@app.get(str_index+'/<_type>/'+str_id+'/_termvectors')
def termvectors_id(m_aa, _index, _type, _id):
    try:
        m_aa.require_permission(':index:crud:read', _index)
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    r = requests.get(
        url=endpoint.endpoint+request.path,
        params=request.query,
        data=request.body,
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


# Get Document and source
@app.get(str_index+'/<_type>/'+str_id)
@app.get(str_index+'/<_type>/'+str_id+'/_source')
def get(m_aa, _index, _type, _id):
    try:
        m_aa.require_permission(':index:crud:read', _index)
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


# Delete document
@app.delete(str_index+'/<_type>/'+str_id)
def delete(m_aa, _index, _type, _id):
    try:
        m_aa.require_permission(':index:crud:delete', _index)
    except BaseError as err:
        response.status = err.status
        return err.errmsg
    r = requests.delete(
        url=endpoint.endpoint+request.path,
        params=request.query
    )
    response.status = r.status_code
    response.set_header('charset', 'UTF8')
    return r.json()


# Update document
@app.put(str_index+'/<_type>/'+str_id)
def update(m_aa, _index, _type, _id):
    try:
        m_aa.require_permission(':index:crud:update', _index)
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


# Scripted Update document
@app.post(str_index+'/<_type>/'+str_id+'/_update')
def update_scripted(m_aa, _index, _type, _id):
    try:
        m_aa.require_permission(':index:crud:update', _index)
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
