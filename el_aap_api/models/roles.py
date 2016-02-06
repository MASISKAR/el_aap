__author__ = 'schlitzer'

import pymongo
import pymongo.errors

from el_aap_api.models.mixins import FilterMixIN, ProjectionMixIn
from el_aap_api.errors import *


class Roles(FilterMixIN, ProjectionMixIn):
    def __init__(self, coll):
        self.defaultfields = {
            '_id': 1,
            'description': 1,
            'users': 1
        }
        self._coll = coll

    def check_ids(self, _ids):
        try:
            count = self._coll.find(
                    filter={'_id': {'$in': _ids}},
                    projection={'id': 1}).count()
            return len(_ids) == count
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)

    def create(self, role):
        try:
            self._coll.insert_one(role)
        except pymongo.errors.DuplicateKeyError:
            raise DuplicateResource(role['_id'])
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)

        return self.get(role['_id'])

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

    def search(self, _ids=None, users=None, fields=None):
        query = {}
        self._filter_builder(query, '_id', _ids, features=['re'])
        self._filter_builder(query, 'users', users, features=['re'])
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
