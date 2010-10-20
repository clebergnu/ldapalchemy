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
schema.py

   Provides Schema related classes
'''

__all__ = ['Schema', 'SchemaCache', 'MetaData', 'OC_NAME', 'AT_NAME', 
           'OC_KIND_ABSTRACT',  'OC_KIND_STRUCTURAL', 'OC_KIND_AUXILIARY']

import re
import ldap
import ldif

from ldapalchemy.config import DefaultConfig
from ldapalchemy.engine import Engine
from ldapalchemy.elements import ElementTypes, ElementClasses

#
# Exceptions
#
class SchemaSourceTypeUknownError(Exception):
    pass
class ElementGotNoOIDError(Exception):
    pass
class ElementHasNoNameError(Exception):
    pass
class ElementHasNoNamesError(Exception):
    pass
class ElementHasSingleNameError(Exception):
    pass
class ElementNotFoundError(Exception):
    pass

#
# Simplified name for elements
# 
OC_NAME = ldap.schema.ObjectClass.schema_attribute    # `objectClasses`
AT_NAME = ldap.schema.AttributeType.schema_attribute  # `attributeTypes`

#
# ObjectClass kind
#
# Here, we comply with what's defined in python ldap module
# OpenLDAP's SDK provides different values, see ldap_schema.h
# 
(OC_KIND_STRUCTURAL,
 OC_KIND_ABSTRACT,
 OC_KIND_AUXILIARY) = range(0, 3)

#
# Regexes
# 

# Matches the OID of a element
# OIDs can also be names and not just numbers. example: nsAdminDomain-oid
GET_ELEMENT_OID_RE = re.compile(r'^\(\s([\w\.-]+)\s.*')
# Returns "'" if the ELEMENT has only on name 
# and returns "(" if it has many
GET_SINGLE_OR_MANY_NAMES_RE = re.compile(r'^\(\s[\w\.-]+\sNAME\s([\'\(]).*')
# Return the element names for elements that have a single name
GET_ELEMENT_NAME_RE = re.compile(r'^\(\s[\w\.-]+\sNAME\s\'(.*?)\'')
# Return the element names for elements that have multiple names
GET_ELEMENT_NAMES_RE = re.compile(r'^\(\s[\w\.-]+\sNAME\s\(\s(.*?)\s\)')

#
# Where the schema whas loaded from
#
(SourceNowhere,
 SourceLdapServer,
 SourceExternalFile) = range(3)

class SchemaLDIFParser(ldif.LDIFParser):
    '''
    Parses a LDIF containing schema information
    Saves information in schema_dn and schema attributes.

    The LDIF associated with a schema, has this kind of format:

    dn: cn=schema
    objectClass: top
    objectClass: ldapSubentry
    objectClass: subschema
    cn: schema
    objectClasses: ( 2.5.6.0 NAME 'top' DESC 'Standard LDAP objectclass' 
     ABSTRACT MUST objectClass X-ORIGIN 'RFC 2256' )
    objectClasses: ( 2.5.20.1 NAME 'subschema' DESC 'Standard LDAP 
     objectclass' SUP top AUXILIARY MAY ( dITStructureRules $ nameForms $ 
     dITContentRules $ objectClasses $ attributeTypes $ matchingRules $ 
     matchingRuleUse ) X-ORIGIN 'RFC 2252' )

    objectClasses is multi-valued attribute, which contains all the
    objectClasses definitions kwnown to this LDAP server. objectClasses
    is one type of ElementType. Other ElemententTypes include attributeTypes
    and matchingRules.

    We are only interested in ElementTypes, as defined in ldapalchemy.element.
    '''
    def __init__(self, file):
        ldif.LDIFParser.__init__(self, file)
        self.load_schema()

    def load_schema(self):
        self.parse()

    def handle(self, dn, entry):
        self.schema_dn = dn
        for key in entry.keys():
            if key not in ElementTypes:
                del(entry[key])
        self.schema_dict = entry

        for key in ElementTypes:
            if key not in self.schema_dict:
                self.schema_dict[key] = []

class SchemaEngineParser:
    '''
    Reads a schema from the subschema subentry of a LDAP server connection
    '''
    def __init__(self, engine):
        self.engine = engine
        self.load_schema()
        
    def load_schema(self):
        self.schema_dn = self.engine._connection.search_subschemasubentry_s()
        if self.schema_dn:
            self.schema_dict = self.engine._connection.\
                read_subschemasubentry_s(self.schema_dn,
                                         ElementTypes)

class SchemaNonCache:
    def __init__(self, source):
        '''
        Represents a LDAP schema 

        self.schema_parser
        ------------------
        This is either a SchemaLDIFParser or a SchemaEngineParser.

        self.schema_source
        ------------------

        The schema's origin. Depending on the provided source, this can hold
        the following values: 

           * SourceNowhere: It's not loaded yet.
           * SourceLdapServer: Comes from a LDAP server
           * SourceExternalFile: Comes from a external LDIF file
        '''
        self.schema_parser = None
        self.schema_source = SourceNowhere

        self.load(source)

    def load(self, source):
        '''
        Loads the source from this schema
        '''
        if type(source) == file:
            self.schema_parser = SchemaLDIFParser(source)
            self.schema_source = SourceExternalFile

        elif type(source) == type(''):
            self.schema_parser = SchemaLDIFParser(open(source))
            self.schema_source = SourceExternalFile
            
        elif isinstance(source, Engine):
            self.schema_parser = SchemaEngineParser(source)
            self.schema_source = SourceLdapServer
        else:
            raise SchemaSourceTypeUknownError

    def get_element_oid(self, element):
        '''
        Returns the OID of a element
        '''
        match = GET_ELEMENT_OID_RE.match(element)
        if match:
            return match.groups()[0]
        raise ElementGotNoOIDError

    def get_element_names(self, element):
        '''
        Returns a list of all names of the given element.

        The result might be a list containing a single item if
        the element has a single name.
        '''
        many_names = self.__element_has_many_names(element)
        if many_names:
            return self.__get_element_names(element)
        else:
            return [self.__get_element_name(element)]

    def get_element_name(self, element):
        '''
        Returns the first name of the given element
        '''
        names = self.get_element_names(element)
        return names[0]

    def get_element_by_oid(self, element_oid, element_type):
        '''
        Returns the element that has the given OID
        '''
        for element in self.schema_parser.schema_dict[element_type]:
            if self.get_element_oid(element) == element_oid:
                return element
        raise ElementNotFoundError

    def get_element_obj_by_oid(self, element_oid, element_type):
        '''
        Returns the element object that has the given OID
        '''
        element = self.get_element_by_oid(element_oid, element_type)
        if element:
            return ElementClasses[element_type](element)

    def get_element_by_name(self, element_name, element_type):
        '''
        Returns the element that has the given element name
        '''
        for element in self.schema_parser.schema_dict[element_type]:
            if element_name in self.get_element_names(element):
                return element
        raise ElementNotFoundError

    def get_element_obj_by_name(self, element_name, element_type):
        '''
        Returns the element object that has the given names
        '''
        element = self.get_element_by_name(element_name, element_type)
        if element:
            return ElementClasses[element_type](element)
        raise ElementNotFoundError

    def get_all_element_oids(self, element_type):
        '''
        Returns all the element oid in this schema
        '''
        result = []
        for element in self.schema_parser.schema_dict[element_type]:
            result.append(self.get_element_oid(element))
        return result

    def get_all_element_names(self, element_type):
        '''
        Returns all names of the element
        '''
        result = []
        for element in self.schema_parser.schema_dict[element_type]:
            element_names = self.get_element_names(element)
            for element_name in element_names:
                result.append(element_name)
        return result

    #
    # Helper methods for Object Classes 
    #
    def get_oc_by_name(self, name):
        return self.get_element_by_name(name, OC_NAME)

    def get_oc_obj_by_name(self, name):
        return self.get_element_obj_by_name(name, OC_NAME)

    def get_oc_by_oid(self, oid):
        return self.get_element_by_oid(oid, OC_NAME)
    
    def get_oc_obj_by_oid(self, oid):
        return self.get_element_obj_by_oid(oid, OC_NAME)

    get_oc = get_oc_by_name
    get_oc_obj = get_oc_obj_by_name

    #
    # Helper methods for Attribute Types
    #
    def get_at_by_name(self, name):
        return self.get_element_by_name(name, AT_NAME)

    def get_at_obj_by_name(self, name):
        return self.get_element_obj_by_name(name, AT_NAME)

    def get_at_by_oid(self, oid):
        return self.get_element_by_oid(oid, AT_NAME)
    
    def get_at_obj_by_oid(self, oid):
        return self.get_element_obj_by_oid(oid, AT_NAME)

    get_at = get_at_by_name
    get_at_obj = get_at_obj_by_name

    #
    # Methods to get extra information for objectClasses elements
    #
    def oc_get_sup_by_name(self, name):
        '''
        Returns the immediate superior objectClass element name
        '''
        obj = self.get_oc_obj(name)
        if obj.sup:
            return obj.sup[0]
        else:
            return None

    oc_get_sup = oc_get_sup_by_name

    def oc_get_all_sup_by_name(self, name, includes_self=False):
        '''
        Returns all superior objectClasses element names for the given oc
        '''
        all_sup = []

        sup = self.oc_get_sup_by_name(name)
        while sup:
            all_sup.append(sup)
            sup = self.oc_get_sup_by_name(sup)

        all_sup.reverse()

        if includes_self:
            all_sup.append(name)
        return all_sup

    oc_get_all_sup = oc_get_all_sup_by_name

    def oc_get_all_sup_obj_by_name(self, name, includes_self=False):
        oc_names = self.oc_get_all_sup_by_name(name, includes_self)
        return [self.get_oc_obj(n) for n in oc_names]

    oc_get_all_sup_obj = oc_get_all_sup_obj_by_name

    def oc_get_all_may_at_by_name(self, name):
        '''
        Return all optional attribute names for the given oc and all sup
        '''
        all_may = []
        ocs = self.oc_get_all_sup_obj_by_name(name, True)
        for oc in ocs:
            all_may += oc.may
        return all_may
    
    oc_get_all_may_at = oc_get_all_may_at_by_name

    def oc_get_all_may_at_obj_by_name(self, name):
        '''
        Return all optional attributes objects for the given oc and all sup
        '''
        at_names = self.oc_get_all_may_at_by_name(name)
        return [self.get_at_obj(n) for n in at_names]

    def oc_get_all_must_at_by_name(self, name):
        all_must = []
        ocs = self.oc_get_all_sup_obj_by_name(name, True)
        for oc in ocs:
            all_must += oc.must
        return all_must

    oc_get_all_must_at = oc_get_all_must_at_by_name

    def oc_get_all_must_at_obj_by_name(self, name):
        at_names = self.oc_get_all_must_at_by_name(name)
        return [self.get_at_obj(n) for n in at_names]

    oc_get_all_must_at_obj = oc_get_all_must_at_obj_by_name

    #
    # Internal Methods
    #

    def __element_has_many_names(self, element):
        '''
        Returns True if the element has many names and False otherwise
        '''
        match = GET_SINGLE_OR_MANY_NAMES_RE.match(element)
        if match:
            result = match.groups()[0]
            if result == "(":
                return True
            elif result == "'":
                return False

    def __get_element_names(self, element):
        '''
        Being assured that the given element has many names, simply return them
        '''
        match = GET_ELEMENT_NAMES_RE.match(element)
        if match:
            names = match.groups()[0]
            names = names.replace("'", "")
            names = names.split()
            return names
    
    def __get_element_name(self, element):
        '''
        Being assured that the given element has a single name, return it
        '''
        match = GET_ELEMENT_NAME_RE.match(element)
        if match:
            name = match.groups()[0]
            return name

class SchemaCacheBase(SchemaNonCache):
    '''
    Implements methods 
    
    This is a base class, use either SchemaStrongCache or SchemaWeakCache.
    DONT USE THIS DIRECTLY. 
    '''
    pass

class SchemaWeakCache(SchemaCacheBase):
    '''
    Improves a Schema by adding a cache for quickly returning entries
    already accessed

    Two WeakKeyDictionary implement these caches:

    * __element_by_name
    * __element_by_oid

    '''
    pass

class SchemaStrongCache(SchemaCacheBase):
    '''
    Improves Schema by adding a cache for quickly returning entries 
    already accessed

    Two dicts implement these caches:

       * __element_by_name
       * __element_by_oid

    SchemaCache sets up these dict to provide faster get_* methods
    
    '''
    def __init__(self, source):
        SchemaCacheBase.__init__(self, source)

        self.__element_by_name = {}
        self.__element_by_oid = {}
        self.__element_obj_by_name = {}
        self.__element_obj_by_oid = {}

        for element_type in ElementTypes:
            self.__element_by_name[element_type] = {}
            self.__element_by_oid[element_type] = {}
            self.__element_obj_by_name[element_type] = {}
            self.__element_obj_by_oid[element_type] = {}

    def get_element_by_oid(self, element_oid, element_type):
        if self.__element_by_oid[element_type].has_key(element_oid):
            return self.__element_by_oid[element_type][element_oid]

        element = SchemaCacheBase.get_element_by_oid(self, 
                                            element_oid, 
                                            element_type)
        if element:
            self.__element_by_oid[element_type][element_oid] = element
            return element

    def get_element_obj_by_oid(self, element_oid, element_type):
        if self.__element_obj_by_oid[element_type].has_key(element_oid):
            return self.__element_obj_by_oid[element_type][element_oid]

        element = SchemaCacheBase.get_element_obj_by_oid(self, 
                                                element_oid, 
                                                element_type)
        if element:
            self.__element_obj_by_oid[element_type][element_oid] = element
            return element

    def get_element_by_name(self, element_name, element_type):
        if self.__element_by_name[element_type].has_key(element_name):
            return self.__element_by_name[element_type][element_name]
        
        element = SchemaCacheBase.get_element_by_name(self, 
                                             element_name, 
                                             element_type)
        if element:
            self.__element_by_name[element_type][element_name] = element
            return element

    def get_element_obj_by_name(self, element_oid, element_type):
        if self.__element_obj_by_name[element_type].has_key(element_oid):
            return self.__element_obj_by_name[element_type][element_oid]

        element = SchemaCacheBase.get_element_obj_by_name(self, 
                                                 element_oid, 
                                                 element_type)
        if element:
            self.__element_obj_by_name[element_type][element_oid] = element
            return element

    def __load_all_element_oids(self, element_type):
        '''
        Loads all element OIDs

        Fetches all OIDs, and then tries to "get" them all. This "get"
        action implemented in this class (SchemaCache), tries to fetch 
        it from the cache, and if not found, from the underlying class
        (Schema).
        '''
        oids = SchemaCacheBase.get_all_element_oids(self, element_type)
        for oid in oids:
            self.get_element_by_oid(oid, element_type)

    def get_all_element_oids(self, element_type):
        self.__load_all_element_oids(element_type)
        return self.__element_by_oid[element_type].keys()
        
    def __load_all_element_names(self, element_type):
        '''
        Loads all element names

        Implements the same logic as __load_all_element_oids
        '''
        names = SchemaCacheBase.get_all_element_names(self, element_type)
        for name in names:
            self.get_element_by_name(name, element_type)

    def get_all_element_names(self, element_type):
        self.__load_all_element_names(element_type)
        return self.__element_by_name[element_type].keys()

#
# The chosen Schema type is SchemaStrongCache (because Weak is not implemented yet)
#
Schema = SchemaStrongCache

#
# SQLALchemy Compatibilty: MetaData is really a Schema
#
if DefaultConfig.compatibility_sqlalchemy_enabled:
    MetaData = Schema
