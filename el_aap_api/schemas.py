__author__ = 'schlitzer'


SAMPLE = {
  "type": "object",
  "additionalProperties": False,
  "properties": {
    "_id": {
      "type": "string",
      "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}"
    },
    "description": {
      "type": "string",
      "required": False
    },
    "users": {
      "type": "array",
      "required": False,
      "items": {
        "type": "string",
        "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
        "uniqueItems": True,
        "enum": [
          "blargggg1",
          "blargggg2"
        ]
      }
    }
  }
}


PERMISSIONS_CREATE = {
    "type": "object",
    "additionalProperties": False,
    "required":  ["_id", "scope"],
    "properties": {
        "_id": {
            "type": "string",
            "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
        },
        "description": {
            "type": "string",
        },
        "permissions": {
            "type": "array",
            "items": {
                "type": "string",
                "uniqueItems": True,
                "enum": [
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
            }
        },
        "roles": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
                "minItems": 0
            }
        },
        "scope": {
            "type": "string"
        }
    }
}

PERMISSIONS_UPDATE = {
    "type": "object",
    "additionalProperties": False,
    "anyOf": [
        {"required": ["description"]},
        {"required": ["permissions"]},
        {"required": ["roles"]},
        {"required": ["scope"]}
    ],
    "properties": {
        "description": {
            "type": "string",
        },
        "permissions": {
            "type": "array",
            "items": {
                "type": "string",
                "uniqueItems": True,
                "enum": [
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
            }
        },
        "roles": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
                "minItems": 0
            }
        },
        "scope": {
            "type": "string"
        }
    }
}

ROLES_CREATE = {
    "type": "object",
    "additionalProperties": False,
    "required":  ["_id"],
    "properties": {
        "_id": {
            "type": "string",
            "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
        },
        "description": {
            "type": "string",
        },
        "users": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
                "minItems": 0
            }
        }
    }
}

ROLES_UPDATE = {
    "type": "object",
    "additionalProperties": False,
    "anyOf": [
        {"required": ["description"]},
        {"required": ["users"]}
    ],
    "properties": {
        "description": {
            "type": "string",
        },
        "users": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
                "minItems": 0
            }
        }
    }
}

SESSIONS_TOKEN = {
    "type": "object",
    "additionalProperties": False,
    "required":  [
        "_id",
        "_token"
    ],
    "properties": {
        "_id": {
            "type": "string"
        },
        "token": {
            "type": "string"
        }
    }
}

USERS_CREATE = {
    "type": "object",
    "additionalProperties": False,
    "required":  [
        "_id",
        "admin",
        "email",
        "name",
        "password"
    ],
    "properties": {
        "_id": {
            "type": "string",
            "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
        },
        "admin": {
            "type": "boolean",
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "name": {
            "type": "string",
        },
        "password": {
            "type": "string",
        }
    }
}

USERS_CREDENTIALS = {
    "type": "object",
    "additionalProperties": False,
    "required":  [
        "password",
        "user"
    ],
    "properties": {
        "password": {
            "type": "string"
        },
        "user": {
            "type": "string",
            "pattern": "^(?!_)[a-zA-Z0-9_\-\.]{8,64}",
        }
    }
}

USERS_UPDATE = {
    "type": "object",
    "additionalProperties": False,
    "anyOf": [
        {"required": ["admin"]},
        {"required": ["email"]},
        {"required": ["name"]},
        {"required": ["password"]},
    ],
    "properties": {
        "admin": {
            "type": "boolean",
        },
        "email": {
            "type": "string",
            "format": "email"
        },
        "name": {
            "type": "string",
        },
        "password": {
            "type": "string",
        }
    }
}
