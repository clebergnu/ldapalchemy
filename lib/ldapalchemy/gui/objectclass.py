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
gui/objectclass.py

   Provides ObjectClass related GUI classes
'''

__all__ = ['ObjectClassList']

import gtk

from ldapalchemy.schema import OC_NAME
from ldapalchemy.elements import ObjectClassElement

class ObjectClassListStore(gtk.ListStore):
    '''
    Hold ObjectClass names
    '''
    def __init__(self, schema):
        '''
        Class init
        '''
        gtk.ListStore.__init__(self, str)

        self.load_from_schema(schema)

    def load_from_schema(self, schema):
        '''
        Load all entries from schema
        '''
        for name in schema.get_all_element_names(OC_NAME):
            self.append([name])

#
# The Text Cell Renderer Singleton
#
text_cell_renderer = gtk.CellRendererText()

#
# The TreeViewColumn for OIDs Singleton
# 
oid_treeview_column = gtk.TreeViewColumn('OID')
oid_treeview_column.pack_start(text_cell_renderer, True)
oid_treeview_column.set_attributes(text_cell_renderer, text=0)

#
# The TreeViewColumn for OIDs Singleton
# 
name_treeview_column = gtk.TreeViewColumn('ObjectClass Name')
name_treeview_column.pack_start(text_cell_renderer, True)
name_treeview_column.set_attributes(text_cell_renderer, text=0)
        
class ObjectClassListView(gtk.TreeView):
    '''
    A list view of Object Classes
    '''
    def __init__(self, schema):
        list_store = ObjectClassListStore(schema)
        gtk.TreeView.__init__(self, list_store)
        self.append_column(name_treeview_column)

class ObjectClassListWindow(gtk.ScrolledWindow):
    '''
    A window that embbeds a ObjectClassListView
    '''
    def __init__(self, schema):
        gtk.ScrolledWindow.__init__(self)

        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.list_view = ObjectClassListView(schema)
        self.add(self.list_view)
        self.set_size_request(300, 480)

class ObjectClassInfo(gtk.VBox):
    '''
    Provides information on a given ObjectClass
    '''
    def __init__(self, element_object):
        assert isinstance(element_object, ObjectClassElement)

        gtk.VBox.__init__(self, 4)

        name_label = gtk.Label(element_object.names[0])
        name_label.show()
        self.pack_start(name_label, False, False)

        sup_label = gtk.Label("\n".join(element_object.sup))
        sup_label.show()
        self.pack_start(sup_label, False, False)

        must_label = gtk.Label("\n".join(element_object.may))
        must_label.show()
        self.pack_start(must_label, True, True)

        self.show_all()

class ObjectClassInfoDlg(gtk.Dialog):
    '''
    Provides a Dialog that embeds a ObjectClassInfo
    '''
    def __init__(self, element_object):
        gtk.Dialog.__init__(self, 
                            title='%s Info' % element_object.names[0],
                            buttons=(gtk.STOCK_CLOSE, gtk.RESPONSE_ACCEPT))

        self.set_size_request(300, 480)

        self.object_class_info = ObjectClassInfo(element_object)
        self.vbox.pack_start(self.object_class_info)


