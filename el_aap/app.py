__author__ = 'schlitzer'

from bottle import Bottle, request, response


# index and document id´s should not start with an underscore
# this is not explicit forbidden by elasticsearch,
# but not recommended, but we do not allow it here.
str_index = '/<_index:re:[a-zA-Z0-9\.]{1}[a-zA-Z0-9_\-\.,]*>'
str_id = '<_id:re:[a-zA-Z0-9\.]{1}[a-zA-Z0-9_\-\.]*>'
#str_index = '/<_index:re:[^_].*>'
#str_id = '<_id:re:[^_].*>'
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
endpoint = Endpoint()


