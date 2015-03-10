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
    'name': 'Project Issue Helpdesk Invoicing',
    'version': '1.0',
    'author' : 'ClearCorp',
    'complexity': 'normal',
    'website': 'http://clearcorp.co.cr',
    'category': 'Invoicing',
    'description': """
Extends Project Issue Helpdesk Invoicing
===============================================

""",
    'depends': ['project_issue_helpdesk','hr_expense','sale_margin','analytic_contract_hr_expense','analytic_user_function','sale_service'],
    'init_xml': [],
    'demo_xml': [],
    'data': ['view/project_issue_helpdesk_invoicing.xml',
             'wizard/project_issue_helpdesk_invoice_wizard.xml'
             ],
    'license': 'AGPL-3',
    'installable': True,
    'active': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: