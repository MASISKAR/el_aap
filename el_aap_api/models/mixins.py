__author__ = 'schlitzer'

import validation

from el_aap_api.errors import *


class ProjectionMixIn(object):
    def _projection(self, fields=None):
        if not fields:
            return self.defaultfields
        fields = fields.split(sep=',')
        for field in fields:
            if field not in self.defaultfields:
                raise InvalidFields('{0} is not a valid field'.format(field))
        result = {}
        for field in fields:
            result[field] = 1
        return result


class FilterMixIN(object):
    def _filter_builder(self, query, field, selector, features=None, validator=None):
        if selector is None:
            return
        if type(selector) is str:
            self._filter_builder_str(query, field, selector, features, validator)
        else:
            self._filter_builder_obj(query, field, selector, features, validator)

    def _filter_builder_obj(self, query, field, selector, features=None, validator=None):
        if type(selector) is list:
            self._filter_builder_list(query, field, selector, validator)

    def _filter_builder_str(self, query, field, selector, features=None, validator=None):
        if 're' in features and selector.startswith('re:'):
            self._filter_builder_re_str(query, field, selector[3:], validator)
        elif 're' not in features and selector.startswith('re:'):
            raise InvalidFields('Regular expression not allowed for: {0}'.format(field))
        else:
            self._filter_builder_list_str(query, field, selector, validator)

    @staticmethod
    def _filter_builder_list(query, field, selector, validator=None):
        if validator:
            try:
                validator(selector)
                query[field] = {'$in': selector}
            except validation.ValidationError as err:
                raise InvalidSelectors(err)
        else:
            query[field] = {'$in': selector}

    def _filter_builder_list_str(self, query, field, selector, validator=None):
        selector = list(set(selector.split(',')))
        self._filter_builder_list(query, field, selector, validator)

    @staticmethod
    def _filter_builder_boolean(query, field, selector):
        if selector in [True, 'true', 'True', '1']:
            selector = True
        elif selector in [False, 'false', 'False', '0']:
            selector = False
        else:
            raise InvalidSelectors('Selector is not a boolean')
        query[field] = selector

    @staticmethod
    def _filter_builder_re_str(query, field, selector, validator=None):
        if validator:
            try:
                validator(selector)
                query[field] = {'$regex': selector}
            except validation.ValidationError as err:
                raise InvalidSelectors(err)
        else:
            query[field] = {'$regex': selector}
