__author__ = 'schlitzer'

import pymongo
import pymongo.errors
import validation

from el_aap_api.models.mixins import FilterMixIN, ProjectionMixIn
from el_aap_api.errors import *


class PermissionsValidator(object):
    def __init__(self):
        v_id = validation.String(regex="^([a-zA-Z0-9]|_|\.|-){8,64}$")
        self.id = v_id.validate
        v_str = validation.String()
        self.str = v_str.validate

        perms_list = validation.List(uniq=True)
        perms_list.validator = validation.Choice(
            choices=[
                ':',
                ':cluster:',
                ':cluster:monitor',
                ':index:',
                ':index:crud:',
                ':index:crud:create',
                ':index:crud:read',
                ':index:crud:update',
                ':index:crud:delete',
                ':index:crud:search',
                ':index:manage:',
                ':index:manage:monitor',
            ]
        )
        self.perms = perms_list.validate

        roles_list = validation.List()
        roles_list.validator = v_id

        create = validation.Dict(ignore_unknown=False)
        create.required['_id'] = v_id
        create.optional['description'] = v_str
        create.optional['permissions'] = perms_list
        create.optional['roles'] = roles_list
        create.required['scope'] = v_str
        self.create = create.validate

        update = validation.Dict(ignore_unknown=False)
        update.optional['description'] = v_str
        update.optional['permissions'] = perms_list
        update.optional['roles'] = roles_list
        update.optional['scope'] = v_str
        self.update = update.validate

        fields = validation.List()
        fields.validator = validation.Choice(choices=[
            '_id',
            'description',
            'permissions',
            'roles',
            'scope'
        ])
        self.fields = fields.validate


class Permissions(FilterMixIN, ProjectionMixIn):
    def __init__(self, coll):
        self.defaultfields = {
            '_id': 1,
            'description': 1,
            'permissions': 1,
            'roles': 1,
            'scope': 1
        }
        self.validate = PermissionsValidator()
        self._coll = coll

    def create(self, permission, chk_roles):
        try:
            self.validate.create(permission)
        except validation.ValidationError as err:
            raise InvalidPostBody(err)
        if 'roles' in permission:
            if not chk_roles(permission['roles']):
                raise InvalidSelectors('some roles missing')
        try:
            self._coll.insert_one(permission)
        except pymongo.errors.DuplicateKeyError:
            raise DuplicateResource(permission['_id'])
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)
        return self.get(permission['_id'])

    def delete(self, _id):
        try:
            self.validate.id(_id)
        except validation.ValidationError:
            raise MalformedResourceID
        try:
            result = self._coll.delete_one(filter={'_id': _id})
        except pymongo.errors.ConnectionFailure as err:
            raise MongoConnError(err)
        if result.deleted_count is 0:
            raise ResourceNotFound(_id)
        return

    def get(self, _id, fields=None):
        try:
            self.validate.id(_id)
        except validation.ValidationError:
            raise MalformedResourceID
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

    def search(self, _ids=None, scope=None, permissions=None, roles=None, fields=None):
        query = {}
        self._filter_builder(query, '_id', _ids, features=['re'])
        self._filter_builder(query, 'permissions', permissions, features=['re'], validator=self.validate.perms)
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

    def update(self, _id, delta, chk_roles):
        try:
            self.validate.id(_id)
        except validation.ValidationError:
            raise MalformedResourceID
        try:
            self.validate.update(delta)
        except validation.ValidationError as err:
            raise InvalidUpdateDocument(err)
        if len(delta) == 0:
            raise InvalidUpdateDocument('empty')
        if 'roles' in delta:
            if not chk_roles(delta['roles']):
                raise InvalidSelectors('some roles missing')
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
