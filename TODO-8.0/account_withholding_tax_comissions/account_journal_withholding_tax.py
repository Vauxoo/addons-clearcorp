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

from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class accountJournalwithholdingTax(orm.Model):
    
     _name = "account.journal"
     _inherit = "account.journal"
     
     _columns = {
        'withholding_tax_required': fields.many2many('account.withholding.tax', 'withholding_tax_journal_required', string="Required Withholding Tax"),
        'withholding_tax_optional': fields.many2many('account.withholding.tax', 'withholding_tax_journal_optional', string="Optional Withholding Tax"),
     }
     
     #Check if the required withholding tax are in optional withholding tax
     def _check_withholding_tax(self, cr, uid, ids, context=None):
         withholding_journal_obj = self.browse(cr, uid, ids[0],context)
                  
         list_required =  []
         list_optional =  []

         for required in withholding_journal_obj.withholding_tax_required:
             list_required.append(required.id)
        
         for optional in withholding_journal_obj.withholding_tax_optional:
             list_optional.append(optional.id)

         for element in list_required:
             if element in list_optional:
                 return False
        
         return True
     
     _constraints = [
        (_check_withholding_tax,'Withholding tax can not be the same for required and optional!',['withholding_tax_required']),
    ]
    