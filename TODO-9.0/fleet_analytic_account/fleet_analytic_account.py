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
from openerp import models, fields, api, _

class FleetVehicle(models.Model):

    _inherit = 'fleet.vehicle'

    @api.model
    def create(self, vals):
        acount_obj=self.env['account.analytic.account']
        fleet_id = super(FleetVehicle, self).create(vals)
        account_id=acount_obj.create({'name':self._vehicle_name_get(fleet_id)})
        fleet_id.write({'analytic_account_id':account_id.id})
        return fleet_id
     
    @api.multi
    def _count_analytic_journal(self):
        account_line_obj = self.env['account.analytic.line']
        self.analytic_journal_count=account_line_obj.search_count([('account_id', '=', self.analytic_account_id.id)])
        
    @api.multi
    def write(self, vals):
        acount_obj=self.env['account.analytic.account']
        res = super(FleetVehicle, self).write(vals)
        if not self.analytic_account_id:
            account_id=acount_obj.create({'name':self._vehicle_name_get(self)})
            self.write({'analytic_account_id':account_id.id})
        self.analytic_account_id.write({'name':self.name})
        return res
    
    @api.multi
    def _vehicle_name_get(self,record):
        res=record.model_id.brand_id.name + '/' + record.model_id.modelname + ' / ' + record.license_plate
        return res
    @api.multi
    def return_analytic_journal_items(self):
            domain = [('account_id','=',self.analytic_account_id.id)]
            return {
                 'type': 'ir.actions.act_window',
                 'name': _('Analytic Journal Items'),
                 'res_model': 'account.analytic.line',
                 'view_type': 'form',
                 'view_mode': 'tree,form',
                 'res_id': self.analytic_account_id.id,
                 'target': 'current',
                 'domain': domain,
                 'nodestroy': True,
                 'flags': {'form': {'action_buttons': True}}

                       }
    
    analytic_account_id = fields.Many2one('account.analytic.account',string='Analytic Account')
    analytic_journal_count = fields.Integer(compute=_count_analytic_journal, string="Analytic Journal" , multi=True)
    