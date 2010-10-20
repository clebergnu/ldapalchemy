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
template.py

   Provides Template For Entering Directory Entries
'''

__all__ = ['Template', 'Table']

from ldapalchemy.config import DefaultConfig
from ldapalchemy.elements import ObjectClassElement, AttributeTypeElement
from ldapalchemy.expression import Add, Modify, Delete, Search
from ldapalchemy.schema import OC_KIND_ABSTRACT, OC_KIND_STRUCTURAL, \
    OC_KIND_AUXILIARY

#
# Exceptions
#
class AttributeNotInObjectClassesError(Exception):
    '''
    Thrown when the given attribute is neither in may or must of a objectClass
    '''
    pass

class RdnAttributeNotSetError(Exception):
    '''
    Thrown when the Relative Distinguished Name is not set
    '''
    pass

#
# Classes used for building templates
#
class ObjectClass:
    '''
    Object Class used in templates
    '''
    def __init__(self, name):
        self.name = name

class AttributeType:
    '''
    AttributeType used in class
    '''
    def __init__(self, name, rdn=False, must=False):
        self.name = name
        self.rdn = rdn
        self.must = must

class Template(object):
    '''
    A template that eases entering directory entries

    Limitations: No multi-value attribute RDN is allowed so far
    '''
    def __init__(self, name, schema, *args):
        '''
        Initializes a new template
        '''
        self.name = name
        self.schema = schema
        self.object_classes = []
        self.attribute_types = []
        self.rdn_attribute_name = None

        #
        # Allow for template to require or allow attributes not defined
        # in the schema
        #
        self.at_extra_may = []
        self.at_extra_must = []

        self.__process_args(args)
        self.__add_sup_ocs()
        self.__reorder_ocs()

    def __process_args(self, args):
        for arg in args:
            if isinstance(arg, ObjectClass):
                oc = self.schema.get_oc_obj_by_name(arg.name)
                self.object_classes.append(oc)
            elif isinstance(arg, AttributeType):
                at = self.schema.get_at_obj_by_name(arg.name)
                self.attribute_types.append(at)

                #
                # Deal with rdn. We use name since a attribute might have
                # multiple names and we want to respect the choice made
                # by the user
                # 
                if arg.rdn:
                    self.rdn_attribute_name = arg.name

        if not self.rdn_attribute_name:
            raise RdnAttributeNameNotSetError

    def __add_sup_ocs(self):
        '''
        Add SUPerior object classes for all oc in this template
        '''
        for oc in self.object_classes:
            oc_name = oc.names[0]
            sup_names = self.schema.oc_get_all_sup_by_name(oc_name)

            for sup_name in sup_names:
                if not self.__has_oc_by_name(sup_name):
                    this_oc = self.schema.get_oc_obj_by_name(sup_name)
                    self.object_classes.append(this_oc)

    def __has_oc_by_name(self, name):
        '''
        Returns True if this template has a oc by this name
        '''
        for oc in self.object_classes:
            if name in oc.names:
                return True
        return False

    def __get_all_may_attribute_names(self):
        '''
        Returns the name of all 'may' attributes in this template's ocs
        '''
        all_may = []
        for oc in self.object_classes:
            all_may += oc.may
        return all_may

    def __get_all_must_attribute_names(self):
        '''
        Returns the name of all 'must' attributes in this template's ocs
        '''
        all_must = []
        for oc in self.object_classes:
            all_must += oc.must
        return all_must

    def __get_all_attribute_names(self):
        '''
        Returns all attribute names mentioned in given object_classes
        '''
        may_attr = self.__get_all_may_attribute_names()
        must_attr = self.__get_all_must_attribute_names()

        return may_attr + must_attr

    def __get_all_object_class_names(self):
        '''
        Return all object classes names 
        '''
        return [oc.names[0] for oc in self.object_classes]

    def __sup_compare(self, oc1, oc2):
        '''
        Compare function for objectClasses with regards to superior classes
        '''
        oc2_all_sup_names = self.schema.oc_get_all_sup(oc2.name)

        if oc1.name in oc2_all_sup_names:
            return -1
        else:
            return 1

    def __reorder_ocs(self):
        '''
        Reorder self.object_classes based on characteristics of them.
        
        ObjectClasses that are "abstract" stay topmost (eg 'top').
        ObjectClasses that are "structural" follow
        ObjectClasses that are "auxiliary" go last
        '''
        abstract_ocs = []       # normally should only have one, 'top'
        structural_ocs = []
        auxiliary_ocs = []

        for oc in self.object_classes:
            if oc.kind == OC_KIND_STRUCTURAL: 
                structural_ocs.append(oc)
            elif oc.kind == OC_KIND_AUXILIARY:
                auxiliary_ocs.append(oc)
            elif oc.kind == OC_KIND_ABSTRACT:
                abstract_ocs.append(oc)

        #
        # Extra love for structural objectClasses: sort them by SUPeriority
        #
        structural_ocs.sort(self.__sup_compare)

        self.object_classes = abstract_ocs + structural_ocs + auxiliary_ocs

    def add(self):
        '''
        Returns an "Add" expression
        '''
        return Add(self)
    insert = add

    def modify(self):
        '''
        Returns a "Modify" expression
        '''
        return Modify(self)
    update = modify

    def delete(self):
        '''
        Returns a "Delete" expression
        '''
        return Delete(self)
    
    def search(self):
        '''
        Returns a "Search" expression
        '''
        return Search(self)

    #
    # Properties
    # 
    object_class_names = property(fget=__get_all_object_class_names,
                                  doc=__get_all_object_class_names.__doc__)

    attribute_names = property(fget=__get_all_attribute_names,
                               doc=__get_all_attribute_names.__doc__)

    attribute_may_names = property(fget=__get_all_may_attribute_names,
                                   doc=__get_all_may_attribute_names.__doc__)

    attribute_must_names = property(fget=__get_all_must_attribute_names,
                                    doc=__get_all_must_attribute_names.__doc__)

#
# SQLAlchemy compatibility
#
if DefaultConfig.compatibility_sqlalchemy_enabled:
    Table = Template
