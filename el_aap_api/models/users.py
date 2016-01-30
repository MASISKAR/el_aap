__author__ = 'schlitzer'

import inspect

from passlib.hash import pbkdf2_sha512
import pymongo
import pymongo.errors
import validation

from el_aap_api.models.mixins import FilterMixIN, ProjectionMixIn
from el_aap_api.errors import *


class UsersValidator(object):
    def __init__(self):
        v_id = validation.String(regex="^([a-zA-Z0-9]|_|\.|-){8,64}$")
        self.id = v_id.validate

        v_str = validation.String()
        self.str = v_str.validate

        credentials = validation.Dict(ignore_unknown=False)
        credentials.required['password'] = v_str
        credentials.required['user'] = v_id
        self.credentials = credentials.validate

        create = validation.Dict(ignore_unknown=False)
        create.required['_id'] = v_id
        create.required['admin'] = validation.Bool()
        create.required['email'] = v_str
        create.required['name'] = v_str
        create.required['password'] = v_str
        self.create = create.validate

        update = validation.Dict(ignore_unknown=False)
        update.optional['admin'] = validation.Bool()
        update.optional['email'] = v_str
        update.optional['name'] = v_str
        update.optional['password'] = v_str
        self.update = update.validate

        fields = validation.List()
        fields.validator = validation.Choice(choices=['_id', 'admin', 'email', 'name'])
        self.fields = fields.validate


class Users(FilterMixIN, ProjectionMixIn):
    def __init__(self, coll):
        self.defaultfields = {
            '_id': 1,
            'admin': 1,
            'email': 1,
            'name': 1
        }
        self.validate = UsersValidator()
        self._coll = coll

    @staticmethod
    def _password(password):
        return pbkdf2_sha512.encrypt(password, rounds=100000, salt_size=32)

    @staticmethod
    def check_basic_auth(request, response):
        user, password = request.auth or (None, None)
        if user or password is None:
            response.set_header('WWW-Authenticate',  'Basic realm="private"')
            raise BasicAuthenticationError
        return user

    def check_credentials(self, credentials=None):
        try:
            self.validate.credentials(credentials)
        except validation.ValidationError as err:
            raise InvalidPostBody(err)
        try:
            password = self._coll.find_one(
                    filter={'_id': credentials['user']},
                    projection={'_id': 0, 'password': 1}
            )
            if not password:
                raise AuthenticationError
            if not pbkdf2_sha512.verify(credentials['password'], password['password']):
                raise AuthenticationError
            return credentials['user']
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)

    def check_ids(self, _ids):
        try:
            count = self._coll.find(
                filter={'_id': {'$in': _ids}},
                projection={'id': 1}).count()
            return len(_ids) == count
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)

    def create(self, user):
        try:
            self.validate.create(user)
        except validation.ValidationError as err:
            raise InvalidPostBody(err)
        try:
            user['password'] = self._password(user['password'])
            self._coll.insert_one(user)
        except pymongo.errors.DuplicateKeyError:
            raise DuplicateResource(user['_id'])
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)
        return self.get(user['_id'])

    def delete(self, user):
        try:
            self.validate.id(user)
        except validation.ValidationError:
            raise MalformedResourceID
        try:
            result = self._coll.delete_one(filter={'_id': user})
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)
        if result.deleted_count is 0:
            raise ResourceNotFound(user)
        return

    def get(self, user, fields=None):
        try:
            self.validate.id(user)
        except validation.ValidationError:
            raise MalformedResourceID
        try:
            result = self._coll.find_one(
                    filter={'_id': user},
                    projection=self._projection(fields)
            )
            if result is None:
                raise ResourceNotFound(user)
            return result
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)

    def is_admin(self, user):
        user = self.get(user, fields='admin')
        if not user['admin']:
            return False
        else:
            return True

    def require_admin(self, user):
        user = self.get(user, fields='admin')
        if not user['admin']:
            raise PermError

    def search(self, _id=None, admin=None, fields=None):
        query = {}
        self._filter_builder(query, '_id', _id, features=['re'])
        self._filter_builder_boolean(query, 'admin', admin)
        try:
            result = []
            for item in self._coll.find(
                    filter=query,
                    projection=self._projection(fields)
            ):
                result.append(item)
            return {'results': result}
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)

    def update(self, user, delta):
        try:
            self.validate.id(user)
        except validation.ValidationError:
            raise MalformedResourceID
        try:
            self.validate.update(delta)
        except validation.ValidationError as err:
            raise InvalidUpdateDocument(err)
        if len(delta) == 0:
            raise InvalidUpdateDocument('empty')
        if 'password' in delta:
            delta['password'] = self._password(delta['password'])
        update = {'$set': {}}
        for k, v in delta.items():
            update['$set'][k] = v
        try:
            result = self._coll.find_one_and_update(
                filter={'_id': user},
                update=update,
                projection=self._projection(),
                return_document=pymongo.ReturnDocument.AFTER
            )
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)
        if result is None:
            raise ResourceNotFound(user)
        return result
