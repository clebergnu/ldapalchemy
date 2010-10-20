# -*- Mode: Python; coding: iso-8859-1 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## This file is part of LDAPAlchemy
## Copyright (C) 2009 Cleber Rodrigues <cleber.gnu@gmail.com>
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
templates.py

   Provides Builtin Templates
'''

__all__ = ['inetOrgPerson', 'posixAccount',]

from ldapalchemy.template import Template, ObjectClass, AttributeType

TEMPLATES = {}

class Templates:
    
    def __init__(self, schema=None):
        self.schema = schema
        self.templates = {}

    def update_schema(self, schema):
        # FIXME: think about method name
        # reload all templates
        self.schema = schema
        for i in self.templates:
            i.schema = self.schema

    def new_template(self, name, object_classes=[], attribute_types=[]):
        template = Template(name, self.schema, object_classes, attribute_types)
        self.update_template(template)

    def update_template(self, template):
        self.templates.update({template.name : template})

    def load_builtin_templates(self):
        
        self.new_template('inetOrgPerson',
                          ObjectClass('inetOrgPerson'),
                          AttributeType('uid', rdn=True))

if __name__ == '__main__':

    from ldapalchemy.engine import Engine
    e = Engine('ldap://127.0.0.1')
    t = Templates(e.schema)
    t.load_builtin_templates()

