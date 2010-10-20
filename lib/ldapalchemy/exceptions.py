# -*- Mode: Python; coding: iso-8859-1 -*-
# vi:si:et:sw=4:sts=4:ts=4

##
## This file is part of LDAPAlchemy
## Copyright (C) 2007, 2008 Cleber Rodrigues <cleber.gnu@gmail.com>
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
exceptions.py

   Provides exceptions used throught ldapalchemy


'''

__all__ = ['EntryAlreadyExists', 
           'AddExpressionEntryAlreadyExists', 
           'AddExpressionAttrNotMay', 
           'AddExpressionAttrNotMust', 
           'NoEngineInTemplateSchema',
           'LDAPInvalidURI', ]

#
# Most of the exceptions exist in python-ldap. The idea here is to isolate 
# this dependency. We might easily switch to Mozilla's LDAP now that
# python-nss is not vaporware anymore.
#

#
# AlreadyExists Hierarchy
#
#
# EntryAlreadyExists
#   |
#   +--AddExpressionEntryAlreadyExists
#
# 

class EntryAlreadyExists(Exception):
    '''
    Entry already exists.

    The DN alreay exists in the given directory server
    '''
    pass

class AddExpressionEntryAlreadyExists(EntryAlreadyExists):
    '''
    Entry already exists when doing an Add operation through an expression

    This further qualifies *when* the exception was thrown
    '''
    pass

class AddExpressionAttrNotMay(Exception):
    '''
    In a Add expression, user provided a attribute that is not allowed
    (present in the "may" list of the template
    '''
    pass

class AddExpressionAttrNotMust(Exception):
    '''
    In a Add expression, user did not provided a value to a mandatory attribute
    '''
    pass

class NoEngineInTemplateSchema(Exception):
    '''
    FIXME
    '''
    pass

class LDAPInvalidURI(Exception):
    '''
    '''
    pass
