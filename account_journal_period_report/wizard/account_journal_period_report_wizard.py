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

from osv import fields, osv

class account_journal_period_report_inherit(osv.osv_memory):

    _inherit = "account.print.journal"
    _name = "account.print.journal"
    _description = "Account Print Journal"
    
    def pre_print_report(self, cr, uid, ids, data, context=None):
        #TODO Pass comments to english
        """
            account.print.journal wizard ya es una herencia del account_common_report. En este wizard se agrega el
            campo sort_selection. Se presenta un error al leer este parámetro, ya que no se pasa de manera correcta
            por lo que se hace un read del campo, para leer de nuevo el parámetro y pasarlo de forma correcta.
            Con esto se soluciona el error.
        """
        data = super(account_journal_period_report_inherit, self).pre_print_report(cr, uid, ids, data, context)
        if context is None:
            context = {}
        vals = self.read(cr, uid, ids,
                         ['sort_selection',],
                         context=context)[0]
        data['form'].update(vals)
        return data

    def _print_report(self, cursor, uid, ids, data, context=None):
        context = context or {}
        # we update form with display account value        
        data = self.pre_print_report(cursor, uid, ids, data, context=context)
                
        return {'type': 'ir.actions.report.xml',
                'report_name': 'account_journal_period_print_inherit',
                'datas': data}

