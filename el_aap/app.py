__author__ = 'schlitzer'

import logging

from bottle import Bottle, request, response


# index and document id´s should not start with an underscore
# this is not explicit forbidden by elasticsearch,
# but not recommended, but we do not allow it here.
str_index = '/<_index:re:[^_].*>'
str_id = '<_id:re:[^_].*>'
#str_index = '/<_index>'
#str_id = '<_id>'


class Endpoint(object):
    def __init__(self):
        self._endpoint = None

    @property
    def endpoint(self):
        return self._endpoint

    @endpoint.setter
    def endpoint(self, endpoint):
        self._endpoint = endpoint

app = Bottle()
app_logger = logging.getLogger('application')
endpoint = Endpoint()


