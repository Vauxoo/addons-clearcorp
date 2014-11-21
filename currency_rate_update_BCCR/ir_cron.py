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

class irCroninherit(orm.Model):
    _inherit = 'ir.cron'
         
    #===========================================================================
    # Overwrite create and write methods. Check if ir_cron is associated with
    # some currency and update automatic_update field in currency.
    # 
    # Overwrite automatic_update in res.currency. If ir_cron is active, then
    # automatic_update in res.currency is active. If ir_cron is inactive, then
    # automatic_update in res.currency is inactive. 
    #
    # This is only for currency that is associated with ir_cron object
    #===========================================================================
    def write(self, cr, uid, ids, vals, context=None):
        dict = {}        
        
        res = super(irCroninherit, self).write(cr, uid, ids, vals, context=context)
        
        for ir_cron in self.browse(cr,uid, ids, context=None):
            currency_id = self.pool.get('res.currency').search(cr, uid,[('ir_cron_job_id','in', [ir_cron.id])], context=context) 
            #Find if cron_job is associated with a currency
            if currency_id:
                #Only if active field is different.
                if 'active' in vals.keys():            
                    dict.update ({'automatic_update':vals['active']})
                    context.update({'from_ir_cron':True})
                    self.pool.get('res.currency').write(cr, uid, currency_id, dict, context=context)
        
        return res
        
    