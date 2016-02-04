__author__ = 'schlitzer'

import re
import threading

from bottle import request, response
from cachetools import TTLCache

from el_aap.app import app_logger
from el_aap_api.errors import *


class AuthenticationAuthorization(object):
    def __init__(self, users, roles, permissions):
        self.cache_user_password = TTLCache(maxsize=10240, ttl=120)
        self.cache_user_password_lock = threading.RLock()
        self.cache_user_roles = TTLCache(maxsize=10240, ttl=120)
        self.cache_user_roles_lock = threading.RLock()
        self.cache_role_permissions = TTLCache(maxsize=10240, ttl=120)
        self.cache_role_permissions_lock = threading.RLock()
        self.cache_permissions = TTLCache(maxsize=10240, ttl=120)
        self.cache_permissions_lock = threading.RLock()
        self.users = users
        self.roles = roles
        self.permissions = permissions

    def check_auth(self):
        user, password = request.auth or (None, None)
        if user is None or password is None:
            response.set_header('WWW-Authenticate',  'Basic realm="private"')
            raise BasicAuthenticationError
        credentials = {
            "user": user,
            "password": password
        }
        with self.cache_user_password_lock:
            if (user, password) in self.cache_user_password:
                return user
        try:
            self.users.check_credentials(credentials)
            with self.cache_user_password_lock:
                self.cache_user_password[(user, password)] = user
            return user
        except AuthenticationError:
            response.set_header('WWW-Authenticate',  'Basic realm="private"')
            raise BasicAuthenticationError

    def get_role_ids_by_user(self, user):
        with self.cache_user_roles_lock:
            if user in self.cache_user_roles:
                return self.cache_user_roles[user]
        roles = list()
        for role in self.roles.search(users=user, fields='_id')['results']:
            roles.append(role['_id'])
        with self.cache_user_roles_lock:
            self.cache_user_roles[user] = roles
        return roles

    def get_permission_ids_by_role(self, role):
        with self.cache_role_permissions_lock:
            if role in self.cache_role_permissions:
                return self.cache_role_permissions[role]
        permissions = list()
        for permission in self.permissions.search(roles=role, fields='_id')['results']:
            permissions.append(permission['_id'])
        with self.cache_role_permissions_lock:
            self.cache_role_permissions[role] = permissions
        return permissions

    def get_permissions(self, permissions):
        cached = list()
        non_cached = list()
        for permission in permissions:
            try:
                with self.cache_permissions_lock:
                    cached.append(self.cache_permissions[permission])
            except KeyError:
                non_cached.append(permission)
        for permission in self.permissions.search(_ids=non_cached, fields='_id,permissions,scope')['results']:
            permission['re'] = re.compile('^'+permission['scope']+'$')
            with self.cache_permissions_lock:
                self.cache_permissions[permission['_id']] = permission
            cached.append(permission)
        return cached

    def get_permissions_by_user(self, user):
        permission_ids = set()
        for role in self.get_role_ids_by_user(user):
            for permission_id in self.get_permission_ids_by_role(role):
                permission_ids.add(permission_id)
        permission_ids = list(permission_ids)
        permissions = self.get_permissions(permission_ids)
        return permissions

    def require_permission(self, permission, index=None):
        user_perms = self.get_permissions_by_user(self.check_auth())
        for perm in user_perms:
            regex = perm['re']
            if index and not regex.match(index):
                continue
            for priv in perm['permissions']:
                if permission.startswith(priv):
                    return True
        raise PermError


