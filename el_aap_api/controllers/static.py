__author__ = 'schlitzer'
from bottle import static_file

from el_aap_api.app import app


@app.route('/elaap/static/<filename:path>')
def server_static(filename):
    return static_file(filename, root='static')
