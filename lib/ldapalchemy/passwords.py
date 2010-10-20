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
passwords.py

   Provides password generation related classes
'''

import sys
import sha
import md5
import random
import base64

from external.ntlm_procs import ldap_nt_password, ldap_lm_password

class BasePassword:
    '''
    Base class for password generation
    '''
    def __init__(self, password_input):
        self.password_input = password_input

    def get_encoded_password(self):
        raise NotImplementedError

    def get_random_salt(self, byte_count):
        '''
        Lame function for generating salts
        '''
        if sys.platform == 'linux2':
            return "".join(open('/dev/random').read(byte_count))
        else:    
            return "".join([chr(random.getrandbits(byte_count)) \
                                for i in range(byte_count)])

class SSHAPassword(BasePassword):
    def __init__(self, password_input):
        self.password_input = password_input

    def get_encoded_password(self):
        salt = self.get_random_salt(8)
        salt = "%8s" % salt
        hash = sha.sha(self.password_input+salt)
        return "{SSHA}" + base64.encodestring(hash.digest()+salt).strip()

class SMD5Password(BasePassword):
    def __init__(self, password_input):
        self.password_input = password_input

    def get_encoded_password(self):
        salt = self.get_random_salt(8)
        salt = "%8s" % salt
        hash = md5.md5(self.password_input+salt)
        return "{SMD5}" + base64.encodestring(hash.digest()+salt).strip()

class LMPassword(BasePassword):
    def __init__(self, password_input):
        self.password_input = password_input

    def get_encoded_password(self):
        return ldap_lm_password(self.password_input)

class NTPassword(BasePassword):
    def __init__(self, password_input):
        self.password_input = password_input

    def get_encoded_password(self):
        return ldap_nt_password(self.password_input)


if __name__ == '__main__':
    print "SSHA", SSHAPassword('blah').get_encoded_password()
    print "SMD5", SMD5Password('blah').get_encoded_password()
    print "NT  ", NTPassword('blah').get_encoded_password()
    print "LM  ", LMPassword('blah').get_encoded_password()

