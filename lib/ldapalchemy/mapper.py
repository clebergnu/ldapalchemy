# -*- Mode: Python; coding: iso-8859-1 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## This file is part of LDAPAlchemy
## Copyright (C) 2007-2009 Cleber Rodrigues <cleber.gnu@gmail.com>
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
mapper.py

   Provides mapper functionality
'''

__all__ = ['mapper', 'Mapper']

from ldapalchemy.template import Template
from ldapalchemy.util import OrderedDict

def mapper(class_, template):
    '''
    Creates a new Mapper object.

    This is simply a function that calls Mapper()
    '''
    return Mapper(class_, template)

class Mapper(object):
    '''
    Maps classes to templates

    As SQLAlchemy says: defines the correlation of class attributes to
    (adjusted) entry attributes.

    Right now we have *no* provision for:
       - Inheritance
       - Poliphormism
       - Extensions
       - <many other things>
    '''
    def __init__(self, class_, template):
        '''
        Creates a new Mapper object.
        '''
        self.class_ = class_
        self.template = template

        if not issubclass(class_, object):
            raise Exception("Class '%s' is not a new-style class" % \
                                class_.__name__)

        if not isinstance(template, Template):
            raise Exception("%s is not a Template instance" % template)

        self.__compile_class()
        self.__compile_properties()

    def __compile_properties(self):
        '''
        Creates properties for Template attributes which have no properties yet
        '''
        self.__props = OrderedDict()

        #
        # For now, no inheritance or custom properties will exist,
        # so all this code does that it creates a one-to-one mapping
        # Template attributes <-> properties
        #
        # 
        
        for attr_name in self.template.attribute_names:
            print "Creating attribute for %s" % attr_name
            self._compile_property(attr_name, attr_name)

    def __compile_class(self):
        '''
        Compiles this class
        '''
        pass

    def _compile_property(self, key, prop, init=True, setparent=True):
        '''
        '''
        # in sqlalchemy, key is just column name, while prop is the 
        # column itself (defined in sqlalchemy.schema#Column)
        #
        # this is major difference from sqlalchemy and ldapalchemy.
        # In sqlalchemy, every column is explicitly defined:
        #
        # Table('name', metadata,
        #       Column('column_name', Integer, ...)
        #
        # In ldapalchemy we assume a lot of implicit attributes:
        #
        # Template('name', metadata,
        #          ObjectClass('person', ...)
        #
        # this alone implies multiple "columns"
        #

#         self.__log("_compile_property(%s, %s)" % (key, prop.__class__.__name__))

#         if not isinstance(prop, MapperProperty):
#             # we were passed a Column or a list of Columns; generate a ColumnProperty
#             columns = util.to_list(prop)
#             column = columns[0]
#             if not expression.is_column(column):
#                 raise exceptions.ArgumentError("%s=%r is not an instance of MapperProperty or Column" % (key, prop))

#             prop = self.__props.get(key, None)

#             if isinstance(prop, ColumnProperty):
#                 # TODO: the "property already exists" case is still not well defined here.
#                 # assuming single-column, etc.

#                 if prop.parent is not self:
#                     # existing ColumnProperty from an inheriting mapper.
#                     # make a copy and append our column to it
#                     prop = prop.copy()
#                 prop.columns.append(column)
#                 #self.__log("appending to existing ColumnProperty %s" % (key))
#             elif prop is None:
#                 mapped_column = []
#                 for c in columns:
#                     mc = self.mapped_table.corresponding_column(c)
#                     if not mc:
#                         raise exceptions.ArgumentError("Column '%s' is not represented in mapper's table.  Use the `column_property()` function to force this column to be mapped as a read-only attribute." % str(c))
#                     mapped_column.append(mc)
#                 prop = ColumnProperty(*mapped_column)
#             else:
#                 if not self.allow_column_override:
#                     raise exceptions.ArgumentError("WARNING: column '%s' not being added due to property '%s'.  Specify 'allow_column_override=True' to mapper() to ignore this condition." % (column.key, repr(prop)))
#                 else:
#                     return

#         if isinstance(prop, ColumnProperty):
#             col = self.mapped_table.corresponding_column(prop.columns[0])
#             # col might not be present! the selectable given to the mapper need not include "deferred"
#             # columns (included in zblog tests)
#             if col is None:
#                 col = prop.columns[0]
#             else:
#                 # if column is coming in after _cols_by_table was initialized, ensure the col is in the 
#                 # right set
#                 if hasattr(self, '_cols_by_table') and col.table in self._cols_by_table and col not in self._cols_by_table[col.table]:
#                     self._cols_by_table[col.table].add(col)

#             self.columns[key] = col
#             for col in prop.columns:
#                 for col in col.proxy_set:
#                     self._columntoproperty[col] = prop
            
                
#         elif isinstance(prop, SynonymProperty) and setparent:
#             if prop.descriptor is None:
#                 prop.descriptor = getattr(self.class_, key, None)
#                 if isinstance(prop.descriptor, Mapper._CompileOnAttr):
#                     prop.descriptor = object.__getattribute__(prop.descriptor, 'existing_prop')
#             if prop.map_column:
#                 if not key in self.mapped_table.c:
#                     raise exceptions.ArgumentError("Can't compile synonym '%s': no column on table '%s' named '%s'"  % (prop.name, self.mapped_table.description, key))
#                 self._compile_property(prop.name, ColumnProperty(self.mapped_table.c[key]), init=init, setparent=setparent)
#         elif isinstance(prop, ComparableProperty) and setparent:
#             # refactor me
#             if prop.descriptor is None:
#                 prop.descriptor = getattr(self.class_, key, None)
#                 if isinstance(prop.descriptor, Mapper._CompileOnAttr):
#                     prop.descriptor = object.__getattribute__(prop.descriptor,
#                                                               'existing_prop')
#         self.__props[key] = prop

#         if setparent:
#             prop.set_parent(self)

#             if not self.non_primary:
#                 setattr(self.class_, key, Mapper._CompileOnAttr(self.class_, key))

#         if init:
#             prop.init(key, self)
        
#         for mapper in self._inheriting_mappers:
#             mapper._adapt_inherited_property(key, prop)



if __name__ == '__main__':

    pass
