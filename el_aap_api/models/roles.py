__author__ = 'schlitzer'

import pymongo
import pymongo.errors
import validation

from el_aap_api.models.mixins import FilterMixIN, ProjectionMixIn
from el_aap_api.errors import *


class RolesValidator(object):
    def __init__(self):
        v_id = validation.String(regex="^([a-zA-Z0-9]|_|\.|-){8,64}$")
        self.id = v_id.validate

        v_str = validation.String()
        self.str = v_str.validate

        user_list = validation.List(uniq=True)
        user_list.validator = v_id

        create = validation.Dict(ignore_unknown=False)
        create.required['_id'] = v_id
        create.optional['description'] = v_str
        create.optional['users'] = user_list
        self.create = create.validate

        update = validation.Dict(ignore_unknown=False)
        update.optional['description'] = v_str
        update.optional['users'] = user_list
        self.update = update.validate

        fields = validation.List()
        fields.validator = validation.Choice(choices=[
            '_id',
            'description',
            'users'
        ])
        self.fields = fields.validate


class Roles(FilterMixIN, ProjectionMixIn):
    def __init__(self, coll):
        self.defaultfields = {
            '_id': 1,
            'description': 1,
            'users': 1
        }
        self.validate = RolesValidator()
        self._coll = coll

    def check_ids(self, _ids):
        try:
            count = self._coll.find(
                    filter={'_id': {'$in': _ids}},
                    projection={'id': 1}).count()
            return len(_ids) == count
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)

    def create(self, role, chk_users):
        try:
            self.validate.create(role)
        except validation.ValidationError as err:
            raise InvalidPostBody(err)
        if 'users' in role:
            if not chk_users(role['users']):
                raise InvalidSelectors('some users missing')
        try:
            self._coll.insert_one(role)
        except pymongo.errors.DuplicateKeyError:
            raise DuplicateResource(role['_id'])
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)

        return self.get(role['_id'])

    def delete(self, role):
        try:
            self.validate.id(role)
        except validation.ValidationError:
            raise MalformedResourceID
        try:
            result = self._coll.delete_one(filter={'_id': role})
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)
        if result.deleted_count is 0:
            raise ResourceNotFound(role)
        return

    def get(self, roles, fields=None):
        try:
            self.validate.id(roles)
        except validation.ValidationError:
            raise MalformedResourceID
        try:
            result = self._coll.find_one(
                    filter={'_id': roles},
                    projection=self._projection(fields)
            )
            if result is None:
                raise ResourceNotFound(roles)
            return result
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)

    def search(self, _id=None, users=None, fields=None):
        query = {}
        self._filter_builder(query, '_id', _id, features=['re'])
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

    def update(self, role, delta, chk_users):
        try:
            self.validate.id(role)
        except validation.ValidationError:
            raise MalformedResourceID
        try:
            self.validate.update(delta)
        except validation.ValidationError as err:
            raise InvalidUpdateDocument(err)
        if len(delta) == 0:
            raise InvalidUpdateDocument('empty')
        if 'users' in delta:
            if not chk_users(delta['users']):
                raise InvalidSelectors('some users missing')
        update = {'$set': {}}
        for k, v in delta.items():
            update['$set'][k] = v
        try:
            result = self._coll.find_one_and_update(
                filter={'_id': role},
                update=update,
                projection=self._projection(),
                return_document=pymongo.ReturnDocument.AFTER
            )
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)
        if result is None:
            raise ResourceNotFound(role)
        return result
