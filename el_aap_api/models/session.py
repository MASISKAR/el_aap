__author__ = 'schlitzer'

import datetime
import uuid

from bson.binary import Binary, STANDARD
from passlib.hash import pbkdf2_sha512
import pymongo
import pymongo.errors
import validation

from el_aap_api.models.mixins import FilterMixIN, ProjectionMixIn
from el_aap_api.errors import *


class SessionValidator(object):
    def __init__(self):
        v_id = validation.StringUUID()
        self.id = v_id.validate

        token = validation.Dict(ignore_unknown=False)
        token.required['_id'] = v_id
        token.required['token'] = v_id
        self.token = token.validate

        fields = validation.List()
        fields.validator = validation.Choice(choices=[
            '_id',
            'lastused',
            'user'
        ])
        self.fields = fields.validate


class Sessions(FilterMixIN, ProjectionMixIn):
    def __init__(self, coll):
        self.defaultfields = {
            '_id': 1,
            'user': 1,
        }
        self.validate = SessionValidator()
        self._coll = coll

    @staticmethod
    def _get_token_from_header(request):
        result = {}
        _id = request.get_header('X-SID', False)
        token = request.get_header('X-TOKEN', False)
        if _id and token:
            result['_id'] = _id
            result['token'] = token
            return result

    @staticmethod
    def _get_token_from_cookie(request):
        result = {}
        _id = request.get_cookie('sid', False)
        token = request.get_cookie('token', False)
        if _id and token:
            result['_id'] = _id
            result['token'] = token
            return result

    def _get_token(self, request):
        token = self._get_token_from_header(request)
        if not token:
            token = self._get_token_from_cookie(request)
        if not token:
            raise TokenError
        else:
            return token

    def check_token(self, token):
        try:
            self.validate.token(token)
        except validation.ValidationError as err:
            raise InvalidPostBody(err)
        try:
            result = self._coll.find_one(
                    filter={'_id': Binary(uuid.UUID(token['_id']).bytes, STANDARD)},
                    projection={'_id': 0, 'token': 1, 'user': 1}
            )
            if not result:
                raise TokenError
            if not pbkdf2_sha512.verify(token['token'], result['token']):
                raise TokenError
            self._coll.update_one(
                filter={'_id': Binary(uuid.UUID(token['_id']).bytes, STANDARD)},
                update={'$set': {'lastused': datetime.datetime.utcnow()}}
            )
            return result['user']
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)

    def create(self, user):
        session = {}
        _id = uuid.uuid4()
        token = uuid.uuid4()
        session['_id'] = Binary(_id.bytes, STANDARD)
        session['token'] = pbkdf2_sha512.encrypt(str(token), rounds=1000, salt_size=32)
        session['lastused'] = datetime.datetime.utcnow()
        session['user'] = user
        try:
            self._coll.insert_one(session)
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)
        result = {
            '_id': str(_id),
            'token': str(token)
        }
        return result

    def delete(self, session):
        try:
            self.validate.id(session)
        except validation.ValidationError:
            raise MalformedResourceID
        try:
            result = self._coll.delete_one(filter={'_id': Binary(uuid.UUID(session).bytes, STANDARD)})
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)
        if result.deleted_count is 0:
            raise ResourceNotFound(session)
        return

    def get(self, session, fields=None):
        try:
            self.validate.id(session)
        except validation.ValidationError:
            raise MalformedResourceID
        try:
            result = self._coll.find_one(
                {
                    '_id': Binary(uuid.UUID(session).bytes, STANDARD)
                },
                self._projection(fields)
            )
            if result is None:
                raise ResourceNotFound(session)
            result['_id'] = session
            if 'lastused' in result:
                result['lastused'] = str(result['lastused'])
            return result
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)

    def get_user(self, request):
        try:
            token = self._get_token(request)
            return self.check_token(token)
        except BaseError:
            raise

    def get_token(self, request):
        try:
            token = self._get_token(request)
            self.check_token(token)
            return token
        except BaseError:
            raise
