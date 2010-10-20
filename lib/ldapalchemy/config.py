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
config.py

   Controls various aspects of ldapalchemy as a library
'''

import os
import sys
import cStringIO

from ConfigParser import ConfigParser

#
# These `constants` control how much of sqlalchemy will me made compatible
#
(COMPATIBILITY_SQLALCHEMY_OFF,
 COMPATIBILITY_SQLALCHEMY_MOST,
 COMPATIBILITY_SQLALCHEMY_ON) = range(3)

COMPATIBILITY_SQLALCHEMY_DESC = {COMPATIBILITY_SQLALCHEMY_OFF : \
                                 'SQLAlchemy compatibility is completely disabled',

                                 COMPATIBILITY_SQLALCHEMY_MOST : \
                                 'Most SQLAlchemy compatibility is enabled',

                                 COMPATIBILITY_SQLALCHEMY_ON : \
                                 'SQLAlchemy compatibility is fully enabled'}
class Config:
    '''
    Controls configurable aspects of LDAPAlchemy
    '''
    def __init__(self):
        self.__compatibility_sqlalchemy_level = COMPATIBILITY_SQLALCHEMY_ON

        self.__connection_uri = "ldap://localhost:389/"
        self.__connection_basedn = ""
        self.__connection_binddn = ""
        self.__connection_bindpw = ""
        
    def __get_compatibility_sqlalchemy_level(self):
        '''
        Returns the level of SQLAlchemy compatibility enabled
        '''
        return self.__compatibility_sqlalchemy_level

    def __get_compatibility_sqlalchemy_enabled(self):
        '''
        Returns whether SQLAlchemy compatibility is enabled or not 

        We only consider it enabled if full compatibility is enabled
        '''
        return (self.__compatibility_sqlalchemy_level == COMPATIBILITY_SQLALCHEMY_ON)

    compatibility_sqlalchemy_level = property(__get_compatibility_sqlalchemy_level)
    compatibility_sqlalchemy_enabled = property(__get_compatibility_sqlalchemy_enabled)

    def __get_connection_uri(self):
        '''
        Return the Uniform Resourse Identifier (URI) of the LDAP connection
        '''
        env_var = "LDAPALCHEMY_CONNECTION_URI"
        if os.environ.has_key(env_var):
            return os.environ[env_var]

        return self.__connection_uri

    connection_uri = property(__get_connection_uri)

    def __get_connection_basedn(self):
        '''
        Returns the base Distinguised Name of the LDAP connection
        '''
        env_var = "LDAPALCHEMY_CONNECTION_BASEDN"
        if os.environ.has_key(env_var):
            return os.environ[env_var]
        
        return self.__connection_basedn

    connection_basedn = property(__get_connection_basedn)


    def __get_connection_binddn(self):
        '''
        Returns the bind Distinguised Name of the LDAP connection
        '''
        env_var = "LDAPALCHEMY_CONNECTION_BINDDN"
        if os.environ.has_key(env_var):
            return os.environ[env_var]
        
        return self.__connection_binddn

    connection_binddn = property(__get_connection_binddn)

    def __get_connection_bindpw(self):
        '''
        Returns the bind password of the LDAP connection
        '''
        env_var = "LDAPALCHEMY_CONNECTION_BINDPW"
        if os.environ.has_key(env_var):
            return os.environ[env_var]
        
        return self.__connection_bindpw

    connection_bindpw = property(__get_connection_bindpw)


class PersistentConfig(Config, ConfigParser):
    '''
    Controls various aspects of LDAPAlchemy as a library

    This class implements persistence using a INI style file (via ConfigParser)
    '''

    SKEL_CONFIG = \
    '''
    [compatibility]
    #valid values are on, off & most
    sqlalchemy = on

    [connection]
    uri = ldap://localhost:389/
    basedn =
    binddn =
    bindpw = 
    '''

    #
    # XXX: Not portable accross non-unix like systems
    #
    GLOBAL_CONF_PATH = '/etc/ldapalchemy.conf'
    USER_CONF_PATH = os.path.expanduser('~/.ldapalchemyrc')

    def __init__(self, filename=None):
        Config.__init__(self)
        ConfigParser.__init__(self)

        # 
        # Load conf: prefer user confs, fallback to global confs
        # 
        if filename is None:
            if os.path.exists(self.USER_CONF_PATH):
                self.filename = self.USER_CONF_PATH
            elif os.path.exists(self.GLOBAL_CONF_PATH):
                self.filename = self.GLOBAL_CONF_PATH

        if filename is None:
            self.__create_skel()
        else:
            self.read(self.filename)

    def __create_skel(self):
        '''
        '''
        pass

    def __get_connection_uri(self):
        env_var = "LDAPALCHEMY_CONNECTION_URI"
        if os.environ.has_key(env_var):
            return os.environ[env_var]

        return self.get('connection', 'uri')

    def __set_connection_uri(self, uri):
        env_var = "LDAPALCHEMY_CONNECTION_URI"
        os.environ[env_var] = uri

        self.set('connection', 'uri', uri)
        self.write(open(self.filename, 'w'))

    connection_uri = property(__get_connection_uri, __set_connection_uri)

    def __get_connection_basedn(self):
        '''
        Returns the base Distinguised Name of the LDAP connection
        '''
        env_var = "LDAPALCHEMY_CONNECTION_BASEDN"
        if os.environ.has_key(env_var):
            return os.environ[env_var]
        
        return self.get('connection', 'basedn')

    connection_basedn = property(__get_connection_basedn)

    def __get_connection_binddn(self):
        '''
        Returns the bind Distinguised Name of the LDAP connection
        '''
        env_var = "LDAPALCHEMY_CONNECTION_BINDDN"
        if os.environ.has_key(env_var):
            return os.environ[env_var]
        
        return self.get('connection', 'binddn')

    connection_binddn = property(__get_connection_binddn)

    def __get_connection_bindpw(self):
        '''
        Returns the bind password of the LDAP connection
        '''
        env_var = "LDAPALCHEMY_CONNECTION_BINDPW"
        if os.environ.has_key(env_var):
            return os.environ[env_var]
        
        return self.get('connection', 'bindpw')

    connection_bindpw = property(__get_connection_bindpw)

    def dump(self):
        self.write(sys.stdout)
        

#
# DefaultConfig Singleton
#
DefaultConfig = PersistentConfig()


if __name__ == '__main__':

    print DefaultConfig
    print DefaultConfig.compatibility_sqlalchemy_level
    print DefaultConfig.compatibility_sqlalchemy_enabled
    print DefaultConfig.connection_uri
    print DefaultConfig.connection_basedn
    print DefaultConfig.connection_binddn
    print DefaultConfig.connection_bindpw
