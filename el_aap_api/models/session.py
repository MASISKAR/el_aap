__author__ = 'schlitzer'

import datetime
import logging
import uuid


from bottle import request
from bson.binary import Binary, STANDARD
from passlib.hash import pbkdf2_sha512

from el_aap_api.models.mixins import FilterMixIN, ProjectionMixIn
from el_aap_api.errors import *


class Sessions(FilterMixIN, ProjectionMixIn):
    def __init__(self, coll):
        self.defaultfields = {
            '_id': 1,
            'user': 1,
        }
        self._coll = coll
        self.log = logging.getLogger('el_aap')

    @method_wrapper
    def _get_token_from_header(self, request):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug('{0} trying to get token from header'.format(request_id))
        result = {}
        _id = request.get_header('X-SID', False)
        token = request.get_header('X-TOKEN', False)
        if _id and token:
            result['_id'] = _id
            result['token'] = token
            self.log.debug('{0} success trying to get token from header'.format(request_id))
            return result
        self.log.debug('{0} failed trying to get token from header'.format(request_id))

    @method_wrapper
    def _get_token_from_cookie(self, request):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug('{0} trying to get token from cookie'.format(request_id))
        result = {}
        _id = request.get_cookie('sid', False)
        token = request.get_cookie('token', False)
        if _id and token:
            result['_id'] = _id
            result['token'] = token
            self.log.debug('{0} success trying to get token from cookie'.format(request_id))
            return result
        self.log.debug('{0} failed trying to get token from cookie'.format(request_id))

    @method_wrapper
    def _get_token(self):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug('{0} trying to get token'.format(request_id))
        token = self._get_token_from_header(request)
        if not token:
            token = self._get_token_from_cookie(request)
        if not token:
            self.log.warn('{0} failed trying to get token'.format(request_id))
            raise TokenError
        else:
            self.log.debug('{0} success trying to get token'.format(request_id))
            return token

    @method_wrapper
    def check_token(self, token):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.debug('{0} checking token {1}'.format(request_id, token['_id']))
        result = self._coll.find_one(
            filter={'_id': Binary(uuid.UUID(token['_id']).bytes, STANDARD)},
            projection={'_id': 0, 'token': 1, 'user': 1}
        )
        if not result:
            self.log.warm('{0} failed checking token {1}, not found in db'.format(request_id, token['_id']))
            raise TokenError
        if not pbkdf2_sha512.verify(token['token'], result['token']):
            self.log.warm('{0} failed checking token {1}, token not matching'.format(request_id, token['_id']))
            raise TokenError
        self._coll.update_one(
            filter={'_id': Binary(uuid.UUID(token['_id']).bytes, STANDARD)},
            update={'$set': {'lastused': datetime.datetime.utcnow()}}
        )
        self.log.debug('{0} success checking token {1}'.format(request_id, token['_id']))
        return result['user']

    @method_wrapper
    def create(self, user):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} creating new session for user {1}'.format(request_id, user))
        session = {}
        _id = uuid.uuid4()
        token = uuid.uuid4()
        session['_id'] = Binary(_id.bytes, STANDARD)
        session['token'] = pbkdf2_sha512.encrypt(str(token), rounds=1000, salt_size=32)
        session['lastused'] = datetime.datetime.utcnow()
        session['user'] = user
        self._coll.insert_one(session)
        result = {
            '_id': str(_id),
            'token': str(token)
        }
        self.log.info('{0} success creating new session for user {1}'.format(request_id, user))
        return result

    @method_wrapper
    def delete(self, _id):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} deleting session {1}'.format(request_id, _id))
        result = self._coll.delete_one(filter={'_id': Binary(uuid.UUID(_id).bytes, STANDARD)})
        if result.deleted_count is 0:
            self.log.warn('{0} session {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        self.log.info('{0} success deleting session {1}'.format(request_id, _id))
        return

    @method_wrapper
    def get(self, _id, fields=None):
        request_id = request.environ.get('REQUEST_ID', None)
        self.log.info('{0} fetching session {1}'.format(request_id, _id))
        result = self._coll.find_one(
            {
                '_id': Binary(uuid.UUID(_id).bytes, STANDARD)
            },
            self._projection(fields)
        )
        if result is None:
            self.log.warn('{0} session {1} not found'.format(request_id, _id))
            raise ResourceNotFound(_id)
        result['_id'] = _id
        if 'lastused' in result:
            result['lastused'] = str(result['lastused'])
        self.log.info('{0} success fetching session {1}'.format(request_id, _id))
        return result

    @method_wrapper
    def get_user(self):
        token = self._get_token()
        return self.check_token(token)

    @method_wrapper
    def get_token(self):
        token = self._get_token()
        self.check_token(token)
        return token
