# -*- coding: utf-8 -*-
##############################################################################
#
#    __terp__.py
#    ccorp_main_company
#    Author: ClearCorp S.A.
#    Copyright (C) 2010 ClearCorp S.A. (<http://www.clearcorp.co.cr>). All Rights Reserved
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
    "name" : "Changes default main company to ClearCorp",
    "version" : "0.1",
    'category': 'Generic Modules/Base',
    "depends" : ['base','l10n_base_data_cr'],
    "author" : "ClearCorp",
    "description": "Changes default main company to ClearCorp",
    'website': 'http://www.clearcorp.co.cr',
    'init_xml': ['ccorp_main_company_data.xml'],
    'update_xml': [],
    'demo_xml': [],
    'installable': True,
    'active': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
