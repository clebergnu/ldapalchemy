# -*- Mode: Python; coding: iso-8859-1 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## This file is part of LDAPAlchemy
## Copyright (C) 2007 Cleber Rodrigues <cleber.gnu@gmail.com>
## All rights reserved
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307,
## USA.
##
## Author(s): Cleber Rodrigues <cleber.gnu@gmail.com>
##
'''
expression.py

   Provides functionality related to add, mod, search expressions
'''

__all__ = ['Add', 'Modify', 'Delete', 'Search']

import ldap

from ldapalchemy.config import DefaultConfig
from ldapalchemy.schema import SchemaEngineParser

from ldapalchemy.exceptions import NoEngineInTemplateSchema
from ldapalchemy.exceptions import AddExpressionAttrNotMay
from ldapalchemy.exceptions import AddExpressionAttrNotMust

class BaseExpression(object):
    '''
    A base for Expression classes

    This is something like "ClauseElement" in SQLAlchemy
    '''
    def _find_engine(self):
        '''
        Tries to find a engine from the underlying template
        '''
        parser = self.template.schema.schema_parser
        if isinstance(parser, SchemaEngineParser):
            return parser.engine
        else:
            raise NoEngineInTemplateSchema

    bind = property(lambda f:f._find_engine())

    def _build_dn(self, basedn, **params):
        key = self.template.rdn_attribute_name
        val = params[key]

        return "%s=%s,%s" % (key, val, basedn)


class Search(BaseExpression):
    def __init__(self, template):
        self.template = template

    def __check_params(self, **params):
        '''
        Deal with parameters passed in as keyword args
        '''
        params['objectClass'] = self.template.object_class_names

        return params

    def __build_filter_string(self, **params):
        '''
        Construct a filters string based on this expression's template
        and supplied params
        '''
        params = self.__check_params(**params)
        params_keys = params.keys()

        filter_items = []

        for k in params_keys:
            v = params[k]
            if type(v) != list:
                v = [v, ]
            for i in v:
                filter_items.append("(%s=%s)" % (k, i))

        filter = "(&%s)" % "".join(filter_items)

        return filter

    def execute(self, basedn, scope=ldap.SCOPE_SUBTREE, **params):
        '''
        Execute a search 
        '''
        filter_string = self.__build_filter_string(**params)
        
        return self.bind._connection.search_s(basedn, scope, filter_string)

class Add(BaseExpression):
    '''
    Provides a Add expression for a template
    '''
    def __init__(self, template):
        self.template = template

    def __check_params(self, **params):
        '''
        Take care of the validity of the params suplied
        '''

        #
        # Every entry is supposed to have a objectClass attribute
        #
        params['objectClass'] = self.template.object_class_names

        #
        # Speed up by caching the keys
        # 
        params_keys = params.keys()

        #
        # Check the attribute name (k) is a allowed attribute
        #
        for k in params_keys:
            if k not in self.template.attribute_names:
                raise AddExpressionAttrNotMay, k

        #
        # Check if all mandatory attributes have values
        # 
        for n in self.template.attribute_must_names:
            if n not in params_keys:
                raise AddExpressionAttrNotMust, n
        
        return params

    def execute(self, basedn, **params):

        params = self.__check_params(**params)

        #
        # Create the modification list to pass to add() method of the 
        # ldap connection
        # 
        mod_list = []
        for k, v in params.items():
            if type(v) != list:
                v = [v,]
            mod_list.append((k, v))

        dn = self._build_dn(basedn, **params)
        
        self.bind._connection.add_s(dn, mod_list)

    def get_as_ldif(self, basedn, **params):
        '''
        Returns what would be done by execute() as LDIF
        '''
        result = []

        #
        # Check `must` and `may` attributes
        #
        params = self.__check_params(**params)

        #
        # First and foremost, goes the distinguished name
        # 
        result.append('dn: %s' % self._build_dn(basedn, **params))

        #
        # Then objectClass, and then rdn attributes
        # 
        param_order = params.keys()
        for n, k in enumerate(('objectClass', self.template.rdn_attribute_name)):
            param_order.remove(k)
            param_order.insert(n, k)

        for k in param_order: 
            v = params[k]
            #
            # FIXME: enforce single_value constraint for attr
            # attr = self.template.schema.get_at_obj(k)
            #
            if type(v) != list:
                v = [v, ]
            for val in v:
                result.append('%s: %s' % (k, val))

        result.append('')
        return "\n".join(result)
    
class Modify(BaseExpression):
    '''
    Provides a update expression for a template
    '''
    def __init__(self, template):
        self.template = template

    def execute(self, basedn, **params):
        pass        

class Delete(BaseExpression):
    '''
    Provides a delete expression for a template
    '''
    def __init__(self, template):
        self.template = template

    def execute(self, basedn, scope=ldap.SCOPE_SUBTREE, **params):
        '''
        FIXME: this should filter stuff to delete based on the template and
        also based on the params supplied. For now, this simply deletes the
        given DN
        '''
        search = Search(self.template)
        search_results = search.execute(basedn, scope, **params)

        dns = [entry[0] for entry in search_results]
        for dn in dns:
            self.bind._connection.delete_s(dn)
    

#
# SQLAlchemy compatibility
#
if DefaultConfig.compatibility_sqlalchemy_enabled:
    Insert = Add
    Select = Search
    Update = Modify
