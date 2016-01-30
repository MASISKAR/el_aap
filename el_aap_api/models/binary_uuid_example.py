__author__ = 'schlitzer'

import uuid

import bson.binary
import pymongo
from pymongo.errors import *
import validation

from el_aap_api.models.mixins import ProjectionMixIn
from el_aap_api.errors import *


class PermissionsValidator(object):
    def __init__(self):
        validate_id = validation.StringUUID()
        self.id = validate_id.validate

        validate_str = validation.String()
        self.str = validate_str.validate
        validate_permission = validation.Dict(ignore_unknown=False)
        validate_permission.required['name'] = validation.String()
        validate_permission.required['description'] = validation.String()
        self.permission_create = validate_permission.validate

        validate_permission_update = validation.Dict(ignore_unknown=False)
        validate_permission_update.optional['description'] = validation.String()
        self.permission_update = validate_permission_update.validate

        validate_fields = validation.List()
        validate_fields.validator = validation.Choice(choices=['description', 'name'])
        self.fields = validate_fields.validate


class Permissions(ProjectionMixIn):
    def __init__(self, database, collection, client=pymongo.MongoClient()):
        self.defaultfields = {
            '_id': 1,
            'description': 1,
            'name': 1
        }
        self.validate = PermissionsValidator()
        self._client = client
        self._db = self._client[database]
        self._permissions = self._db[collection]

    def get(self, permission_id, fields=None):
        try:
            self.validate.id(permission_id)
        except validation.ValidationError:
            raise MalformedResourceID
        try:
            result = self._permissions.find_one(
                {'_id': bson.binary.UUID(uuid.UUID(permission_id).hex)},
                self._projection(fields)
            )
            if result is None:
                raise ResourceNotFound(permission_id)
            result['_id'] = str(result['_id'])
            return result
        except ServerSelectionTimeoutError:
            return

    def create(self, permission):
        try:
            self.validate.permission_create(permission)
        except validation.ValidationError as err:
            raise InvalidPostBody(err)

        permission['_id'] = bson.binary.UUID(uuid.uuid4().hex)

        try:
            self._permissions.insert_one(permission)
        except DuplicateKeyError:
            raise DuplicateResource(permission['name'])

        return self.get(str(permission['_id']))

    def update(self, permission_id, delta):
        try:
            self.validate.id(permission_id)
        except validation.ValidationError:
            raise MalformedResourceID
        try:
            self.validate.permission_update(delta)
        except validation.ValidationError as err:
            raise InvalidUpdateDocument(err)
        if len(delta) == 0:
            raise InvalidUpdateDocument('empty')
        update = {'$set':  {}}
        for k, v in delta.items():
            update['$set'][k] = v
        result = self._permissions.find_one_and_update(
            filter={'_id': bson.binary.UUID(uuid.UUID(permission_id).hex)},
            update=update,
            projection=self._projection(),
            return_document=pymongo.ReturnDocument.AFTER
        )
        if result is None:
            raise ResourceNotFound(permission_id)
        result['_id'] = str(result['_id'])
        return result

    def delete(self, permission_id):
        try:
            self.validate.id(permission_id)
        except validation.ValidationError:
            raise MalformedResourceID
        result = self._permissions.delete_one(
            {'_id': bson.binary.UUID(uuid.UUID(permission_id).hex)}
        )
        if result.deleted_count is 0:
            raise ResourceNotFound(permission_id)
        return
