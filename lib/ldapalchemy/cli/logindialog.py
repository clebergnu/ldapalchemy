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

__all__ = ['LdapLoginDlg']

import ldap
import ldapurl
import getpass

from ldapalchemy.engine import Engine
from ldapalchemy.config import DefaultConfig
from ldapalchemy.exceptions import LDAPInvalidURI

class LdapLoginDialog:
    '''
    A LoginDlg that attempts to establish a connection to a LDAP server
    '''
    def __init__(self):
        self.config = DefaultConfig

    def __create_engine(self):
        '''
        Creates the engine. Usually called by run()
        '''
        try:
            self.engine = Engine(self.config.connection_uri,
                                 binddn=self.config.connection_binddn,
                                 bindpw=self.config.connection_bindpw)
            
        except ldap.NO_SUCH_OBJECT:
            pass
        except ldap.INVALID_CREDENTIALS:
            pass

    def __input_connection_uri(self):
        '''
        Asks for the connection uri
        '''
        uri = raw_input('Enter LDAP server URI [%s]: ' \
                        % self.config.connection_uri)

        if not uri:
            return self.config.connection_uri

        if not ldapurl.isLDAPUrl(uri):
            raise LDAPInvalidURI
            
        return uri

    def __input_connection_binddn(self):
        '''
        Asks for the connection binddn
        '''
        binddn = raw_input('Enter the bind DN [%s]: ' \
                           % self.config.connection_binddn)
        return binddn

    def __input_connection_bindpw(self):
        '''
        Asks for the connection binddn
        '''
        bindpw = getpass.getpass('Enter the bind password [********]: ')

        return bindpw

    def __input_connection(self):
        try:
            print 'Connecting to LDAP server...'
            self.config.connection_uri = self.__input_connection_uri()
            self.config.connection_binddn = self.__input_connection_binddn()
            self.config.connection_bindpw = self.__input_connection_bindpw()

        except KeyboardInterrupt:
            print 'Cancelled!'

        except LDAPInvalidURI:
            print 'Error: Invalid LDAP URI! Exiting...'
            raise SystemExit

    def run(self):
        self.__input_connection()
        self.__create_engine()

        return self.engine

if __name__ == '__main__':

    l = LdapLoginDialog()
    l.run()
