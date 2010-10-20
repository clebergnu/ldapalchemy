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

__all__ = ['LdapLoginDlg']

import gtk
import ldap
import ldapurl

from ldapalchemy.engine import Engine

class LdapLoginDlg(gtk.Dialog):
    '''
    A LoginDlg that attempts to establish a connection to a LDAP server
    '''
    def __init__(self, parent=None):
        gtk.Dialog.__init__(self, 
                            title='LDAP Server Login',
                            parent=parent,
                            flags=0,
                            buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        #
        # GNOME HIG compliance
        #
        self.set_border_width(5)
        self.vbox.set_border_width(2)
        self.vbox.set_spacing(6)

        #
        # UI Widgets
        #
        self.uri_label = gtk.Label('URI:')
        self.uri_entry = gtk.Entry()
        self.uri_entry.set_text('ldap://localhost')

        self.dn_label = gtk.Label('DN:')
        self.dn_entry = gtk.Entry()
        self.password_label = gtk.Label('Password:')
        self.password_entry = gtk.Entry()
        self.password_entry.set_visibility(False)

        self.set_default_response(gtk.RESPONSE_ACCEPT)
        self.uri_entry.set_activates_default(True)
        self.dn_entry.set_activates_default(True)
        self.password_entry.set_activates_default(True)

        self.status_bar = gtk.Statusbar()

        #
        # UI Widgets packing
        # 
        self.main_table = gtk.Table(2, 3)
        self.main_table.attach(self.uri_label,
                               0, 1, 0, 1, xoptions=gtk.FILL)
        self.main_table.attach(self.uri_entry,
                               1, 2, 0, 1, xoptions=gtk.FILL|gtk.EXPAND)
        self.main_table.attach(self.dn_label,
                               0, 1, 1, 2, xoptions=gtk.FILL)
        self.main_table.attach(self.dn_entry,
                               1, 2, 1, 2, xoptions=gtk.FILL|gtk.EXPAND)
        self.main_table.attach(self.password_label,
                               0, 1, 2, 3, xoptions=gtk.FILL)
        self.main_table.attach(self.password_entry,
                               1, 2, 2, 3, xoptions=gtk.FILL|gtk.EXPAND)
        self.vbox.pack_start(self.main_table)

        #
        # The Engine (LDAP Connection)
        # 
        self.engine = None

    def _create_engine(self):
        '''
        Creates the engine. Usually called by run()
        '''
        uri = self.uri_entry.get_text()

        try:
            self.engine = Engine(self.uri_entry.get_text(),
                                 user=self.dn_entry.get_text(),
                                 passwd=self.password_entry.get_text())
        except ldap.NO_SUCH_OBJECT:
            pass
        except ldap.INVALID_CREDENTIALS:
            pass


    def run(self):
        self.show_all()
        self.dn_entry.grab_focus()
        result = gtk.Dialog.run(self)

        if result == gtk.RESPONSE_ACCEPT:
            self._create_engine()
        
        self.destroy()
        return result

if __name__ == '__main__':
    w = LdapLoginDlg()
    w.run()
