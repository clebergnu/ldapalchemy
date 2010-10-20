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
elements.py

   Definition of LDAP Elements that make up a schema (metadata)
'''

__all__ = ['ObjectClassElement',
           'AttributeTypeElement',
           'ElementTypes',
           'ElementClasses' ]

'''

The following Elements could be created in the future:
 - LdapSyntaxElement
 - MatchingRule
 - MatchingRuleUse
 - DITContentRules
 - DITStructureRule
 - NameForm

Python ldap module X LDAPAlchemy
-------------------X---------------------
SchemaElement      X Element
ObjectClass        X ObjectClassElement
AttributeType      X AttributeTypeElement

'''

import ldap

from ldap.schema.models import SchemaElement
from ldap.schema.models import ObjectClass as LDAPObjectClass
from ldap.schema.models import AttributeType as LDAPAttributeType
from ldap.schema.tokenizer import split_tokens, extract_tokens

class Element(object, SchemaElement):
    '''
    An LDAP Element
    '''
    def __init__(self, element_line):
        object.__init__(self)
        SchemaElement.__init__(self)

        self.load_from_schema_element_line(element_line)
        self.name = self.names[0]

    def load_from_schema_element_line(self, element_line):
        '''
        Populates attributes from a schema element line
        '''
        split_list = split_tokens(element_line, None)
        tokens_dict = extract_tokens(split_list, self.token_defaults)

        self.set_id(split_list[1])
        
        self._set_attrs(split_list, tokens_dict)

    def __repr__(self):
        return '%s: %s (oid: %s)' % (self.__class__.__name__,
                                     self.name,
                                     self.oid)

class AttributeTypeElement(Element, LDAPAttributeType):
    '''
    An LDAP AttributeType Element

    This represents the schema for a given LDAP attribute.
    '''
    def __init__(self, element_line):
        Element.__init__(self, element_line)
        LDAPAttributeType.__init__(self)

class ObjectClassElement(Element, LDAPObjectClass):
    def __init__(self, element_line):
        Element.__init__(self, element_line)
        LDAPObjectClass.__init__(self)

#
# This is like ldap.subentry.SCHEMA_ATTRS, but somewhat better named, IMHO
# 
ElementTypes = (ldap.schema.ObjectClass.schema_attribute,
                ldap.schema.AttributeType.schema_attribute,
                ldap.schema.LDAPSyntax.schema_attribute,
                ldap.schema.MatchingRule.schema_attribute,
                ldap.schema.MatchingRuleUse.schema_attribute,
                ldap.schema.DITContentRule.schema_attribute,
                ldap.schema.DITStructureRule.schema_attribute,
                ldap.schema.NameForm.schema_attribute)


#
# The classes for each Element Type
#
ElementClasses = { \
    ldap.schema.AttributeType.schema_attribute : AttributeTypeElement,
    ldap.schema.ObjectClass.schema_attribute : ObjectClassElement,
    }

