__author__ = 'schlitzer'


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


class MalformedResourceID(ValidationError):
    def __init__(self):
        super().__init__(
            status=400,
            code=3001,
            msg="Malformed resource ID"
        )


class InvalidPostBody(ValidationError):
    def __init__(self, err):
        super().__init__(
                status=400,
                code=3002,
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


class InvalidUpdateDocument(ValidationError):
    def __init__(self, err):
        super().__init__(
                status=400,
                code=3005,
                msg="Invalid update document: {0}".format(err)
        )
