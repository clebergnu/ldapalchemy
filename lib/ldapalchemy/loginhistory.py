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
loginhistory.py

   Provides a history of `logins` to LDAP directories
'''

__all__ = ['LoginHistory']

import os
import os.path
import xml.dom.minidom

LOGIN_HISTORY_PATH = os.path.expanduser('~/.ldapalchemy_login_history')

class LoginHistory:
    '''
    Controls previous logins
    '''
    def __init__(self, path=LOGIN_HISTORY_PATH):
        self.path = path

        if not os.path.exists(self.path):
            self.create_empty_file()

        self.dom = xml.dom.minidom.parse(self.path)
        self.dom_doc = self.dom.documentElement

    def create_empty_file(self):
        '''
        Creates a new login history file
        '''
        impl = xml.dom.minidom.getDOMImplementation()
        newdoc = impl.createDocument(None, "loginhistory", None)
        newdoc.writexml(open(LOGIN_HISTORY_PATH, 'w'))

    def get_hosts(self):
        '''
        Return hosts name
        '''
        result = []
        
        hosts = self.dom_doc.getElementsByTagName('host')
        for host in hosts:
            result.append(host.getAttribute('name'))

        return result

    def get_users(self, host_name):
        
        hosts = self.dom_doc.getElementsByTagName('host')
        for host in hosts:
            if host_name == host.getAttribute('name'):
                return [u.getAttribute('name') for u in \
                            host.getElementsByTagName('user')]


if __name__ == '__main__':

    lh = LoginHistory()
    for host in lh.get_hosts():
        print 'Host:', host
        print 'Users:', ",".join(lh.get_users(host))

