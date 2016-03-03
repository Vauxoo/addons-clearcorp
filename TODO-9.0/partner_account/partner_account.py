# -*- coding: utf-8 -*-
##############################################################################
#
# OpenERP, Open Source Management Solution
# Addons modules by CLEARCORP S.A.
# Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, _

class ProductTemplate(models.Model):
    _inherit='product.template'

    line_ids = fields.One2many('partner.account.line', 'product_id', string='Accounts Lines')

class PartnerAccount(models.Model):
    _name= 'partner.account'
    
    partner_id = fields.Many2one('res.partner',string='Partner',required=True)
    ref = fields.Char(related='partner_id.ref',string='Contact Reference')
    line_ids = fields.One2many('partner.account.line', 'partner_account_id', string='Accounts Lines')
    
    _sql_constraints = [
        ('partner_account_unique',
        'UNIQUE(partner_id)',
        'Partner account already exist for this partner')]
    
    _rec_name='partner_id'
     
class PartnerAccountLines(models.Model):
    _name= 'partner.account.line'
    
    code=fields.Char(string='Code',required=True)
    name=fields.Char(string='Name',required=True)
    product_id = fields.Many2one('product.template',string='Product',required=True)
    partner_account_id = fields.Many2one('partner.account',string='Partner Account')
    partner_id = fields.Many2one(related='partner_account_id.partner_id',string='Partner')