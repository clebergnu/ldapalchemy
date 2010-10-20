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
engine.py

   Provides a create_engine function
'''

__all__ = ['Engine', 'create_engine']

import ldap
import ldapurl

class Engine:
    def __init__(self, url, **kwargs):
        if not ldapurl.isLDAPUrl(url):
            #
            # assume a hostname or ip address
            #
            url = 'ldap://%s' % url

        self.url = url
        self._initialize()

        self._username = ''
        self._password = ''

        #
        # Process kwargs
        # 
        for key in ('user', 'username', 'binddn'):
            if kwargs.has_key(key):
                self._username = kwargs[key]
                break

        for key in ('passwd', 'password', 'bindpw'):
            if kwargs.has_key(key):
                self._password = kwargs[key]
                break

        self._bind()

    def _initialize(self):
        '''
        Setup the actual connection to the LDAP directory
        '''
        self._connection = ldap.initialize(self.url)
        self._connection.protocol_version = ldap.VERSION3

    def _bind(self):
        '''
        Bind to the LDAP directory
        '''
        self._bind_status = self._connection.bind_s(self._username,
                                                    self._password)


def create_engine(url, **kwargs):
    '''
    Creates an engine to the LDAP Directory
    '''
    return Engine(url, **kwargs)
