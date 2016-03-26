__author__ = 'schlitzer'

import logging

from el_aap.app import app

app_logger = logging.getLogger('el_aap')


@app.get('/_plugin/<dummy:path>')
def get(m_aa, m_elproxy, dummy=None):
    m_aa.require_permission(':', '')
    return m_elproxy.get()


@app.post('/_plugin/<dummy:path>')
def post(m_aa, m_elproxy, dummy=None):
    m_aa.require_permission(':', '')
    return m_elproxy.post()


@app.put('/_plugin/<dummy:path>')
def put(m_aa, m_elproxy, dummy=None):
    m_aa.require_permission(':', '')
    return m_elproxy.put()


@app.delete('/_plugin/<dummy:path>')
def delete(m_aa, m_elproxy, dummy=None):
    m_aa.require_permission(':', '')
    return m_elproxy.delete()

