# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Project Reports',
    'version': '1.0',
    'url': 'http://launchpad.net/openerp-ccorp-addons',
    'author': 'ClearCorp S.A.',
    'website': 'http://clearcorp.co.cr',
    'category': 'Project Management',
    'complexity': 'normal',
    'description': """This module adds project reports
    """,
    'depends': [
                    'report_webkit_lib',
                    'project_extended',
                    ],
    'init_xml': [],
    'demo_xml': [],
    'update_xml': [
                    'report/report.xml',
                    'wizard/project_report_wizard.xml',
                    'report_menus.xml',
                    ],
    'license': 'AGPL-3',
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
