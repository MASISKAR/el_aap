__author__ = 'schlitzer'

from passlib.hash import pbkdf2_sha512
import pymongo
import pymongo.errors

from el_aap_api.models.mixins import FilterMixIN, ProjectionMixIn
from el_aap_api.errors import *


class Users(FilterMixIN, ProjectionMixIn):
    def __init__(self, coll):
        self.defaultfields = {
            '_id': 1,
            'admin': 1,
            'email': 1,
            'name': 1
        }
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
        user['password'] = self._password(user['password'])
        try:
            self._coll.insert_one(user)
        except pymongo.errors.DuplicateKeyError:
            raise DuplicateResource(user['_id'])
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)
        return self.get(user['_id'])

    def delete(self, _id):
        try:
            result = self._coll.delete_one(filter={'_id': _id})
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)
        if result.deleted_count is 0:
            raise ResourceNotFound(_id)
        return

    def get(self, _id, fields=None):
        try:
            result = self._coll.find_one(
                    filter={'_id': _id},
                    projection=self._projection(fields)
            )
            if result is None:
                raise ResourceNotFound(_id)
            return result
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)

    def is_admin(self, _id):
        _id = self.get(_id, fields='admin')
        if not _id['admin']:
            return False
        else:
            return True

    def require_admin(self, user):
        user = self.get(user, fields='admin')
        print(user)
        if not user['admin']:
            raise PermError

    def search(self, _ids=None, admin=None, fields=None):
        query = {}
        self._filter_builder(query, '_id', _ids, features=['re'])
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

    def update(self, _id, delta):
        if 'password' in delta:
            delta['password'] = self._password(delta['password'])
        update = {'$set': {}}
        for k, v in delta.items():
            update['$set'][k] = v
        try:
            result = self._coll.find_one_and_update(
                filter={'_id': _id},
                update=update,
                projection=self._projection(),
                return_document=pymongo.ReturnDocument.AFTER
            )
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)
        if result is None:
            raise ResourceNotFound(_id)
        return result
