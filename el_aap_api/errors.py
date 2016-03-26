__author__ = 'schlitzer'
import logging
from bottle import request, response
import jsonschema.exceptions
import requests.packages.urllib3.exceptions

__all__ = [
    'error_catcher',
    'method_wrapper',
    'AlreadyAuthenticatedError',
    'AuthenticationError',
    'BaseError',
    'BasicAuthenticationError',
    'DuplicateResource',
    'InvalidBody',
    'InvalidFields',
    'InvalidSelectors',
    'ModelError',
    'MongoConnError',
    'PermError',
    'ResourceNotFound',
    'TokenError',
    'ValidationError'
]


def error_catcher(func):
    def wrapper(*args, **kwargs):
        log = logging.getLogger('el_aap')
        request_id = request.environ.get('REQUEST_ID', None)
        try:
            try:
                log.debug("entering module {0} function {1} request {2}".format(
                    func.__module__, func.__name__, request_id)
                )
                return func(*args, **kwargs)
            except jsonschema.exceptions.ValidationError as err:
                raise InvalidBody(err)
            except requests.packages.urllib3.exceptions.HTTPError as err:
                log.error('error communicating with ElasticSearch instance, request {0}'.format(request_id))
                raise ElasticSearchConnError(err)
            finally:
                log.debug("leaving module {0} function {1} request {2}".format(
                    func.__module__, func.__name__, request_id)
                )
        except BaseError as err:
            response.status = err.status
            return err.errmsg
    return wrapper


def method_wrapper(func):
    def wrapper(self, *args, **kwargs):
        log = logging.getLogger('el_aap')
        request_id = request.environ.get('REQUEST_ID', None)
        log.debug("entering {0} method {1} request {2}".format(
            self.__class__, func.__name__, request_id
        ))
        try:
            return func(self, *args, **kwargs)
        finally:
            log.debug("leaving {0} method {1} request {2}".format(
                self.__class__, func.__name__, request_id
            ))
    return wrapper


class BaseError(Exception):
    def __init__(self, status, code, msg):
        self.status = status
        self.msg = msg
        self.code = code
        self.errmsg = {
            "code": self.code,
            "msg": self.msg
        }


class MongoConnError(BaseError):
    def __init__(self, err):
        super().__init__(
            status=500,
            code=1001,
            msg="MongoDB connection error: {0}".format(err)
        )


class ElasticSearchConnError(BaseError):
    def __init__(self, err):
        super().__init__(
            status=500,
            code=1002,
            msg="ElasticSearch connection error: {0}".format(err)
        )


class ModelError(BaseError):
    pass


class ValidationError(BaseError):
    pass


class AuthenticationError(ModelError):
    def __init__(self):
        super().__init__(
                status=403,
                code=1001,
                msg="Invalid username or Password"
        )


class BasicAuthenticationError(ModelError):
    def __init__(self):
        super().__init__(
            status=401,
            code=1002,
            msg="Invalid username or Password"
        )


class AlreadyAuthenticatedError(ModelError):
    def __init__(self):
        super().__init__(
                status=403,
                code=1003,
                msg="Already authenticated"
        )


class TokenError(ModelError):
    def __init__(self):
        super().__init__(
            status=403,
            code=1004,
            msg="Invalid or expired token"
        )


class PermError(ModelError):
    def __init__(self):
        super().__init__(
            status=403,
            code=1005,
            msg="Required permission missing"
        )


class ResourceNotFound(ModelError):
    def __init__(self, user_id):
        super().__init__(
            status=404,
            code=2001,
            msg="No resource with ID {0} found".format(user_id)
        )


class DuplicateResource(ModelError):
    def __init__(self, resource):
        super().__init__(
            status=400,
            code=2002,
            msg="Duplicate Resource: {0}".format(resource)
        )


class InvalidBody(ValidationError):
    def __init__(self, err):
        super().__init__(
                status=400,
                code=3001,
                msg="Invalid post body: {0}".format(err)
        )


class InvalidFields(ValidationError):
    def __init__(self, err):
        super().__init__(
                status=400,
                code=3003,
                msg="Invalid field selection: {0}".format(err)
        )


class InvalidSelectors(ValidationError):
    def __init__(self, err):
        super().__init__(
                status=400,
                code=3004,
                msg="Invalid selection: {0}".format(err)
        )
