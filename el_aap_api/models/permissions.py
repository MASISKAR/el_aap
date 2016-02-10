__author__ = 'schlitzer'

import pymongo
import pymongo.errors
import validation

from el_aap_api.models.mixins import FilterMixIN, ProjectionMixIn
from el_aap_api.errors import *


class Permissions(FilterMixIN, ProjectionMixIn):
    def __init__(self, coll):
        self.defaultfields = {
            '_id': 1,
            'description': 1,
            'permissions': 1,
            'roles': 1,
            'scope': 1
        }
        self._coll = coll

    def add_permissions(self, _id, permissions):
        update = {'$addToSet': {"permissions": {"$each": permissions}}}
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

    def add_roles(self, _id, roles):
        update = {'$addToSet': {"roles": {"$each": roles}}}
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

    def create(self, permission):
        try:
            self._coll.insert_one(permission)
        except pymongo.errors.DuplicateKeyError:
            raise DuplicateResource(permission['_id'])
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)
        return self.get(permission['_id'])

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
            result['_id'] = _id
            return result
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)

    def remove_permissions(self, _id, permissions):
        update = {"$pullAll": {"permissions": permissions}}
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

    def remove_roles(self, _id, roles):
        update = {"$pullAll": {"roles": roles}}
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

    def remove_role_from_all(self, role):
        try:
            self._coll.update_many(
                filter={"roles": role},
                update={"$pull": {"roles": role}}
            )
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)

    def search(self, _ids=None, scope=None, permissions=None, roles=None, fields=None):
        query = {}
        self._filter_builder(query, '_id', _ids, features=['re'])
        self._filter_builder(query, 'permissions', permissions, features=['re'])
        self._filter_builder(query, 'scope', scope, features=['re'])
        self._filter_builder(query, 'roles', roles, features=['re'])
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
        try:
            result = self._coll.find_one_and_update(
                filter={'_id': _id},
                update={'$set': delta},
                projection=self._projection(),
                return_document=pymongo.ReturnDocument.AFTER
            )
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)
        if result is None:
            raise ResourceNotFound(_id)
        result['_id'] = _id
        return result
