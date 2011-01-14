# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution	
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>). All Rights Reserved
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    "name" : "Accounting module",
    "version" : "1.1",
    "author" : "Clearcorp",
    "category" : "Generic Modules/Accounting",
    "website" : "http://www.openerp.com",
    "description": "Fix account.invoice: period for multi company  and sets the invoice number to the description of the invoice if description doesnt have any",
    'author': 'ClearCorp',
    'website': 'http://www.openerp.com',
    'depends': ["base","account"],
    'init_xml': [],
    'installable': True,
    'active': False
    
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
