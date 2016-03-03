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

from openerp import models, fields

class AccountAssetAsset(models.Model):

    _inherit = ['account.asset.asset', 'mail.thread']
    _name = 'account.asset.asset'

    _track = {
        'state': {
            'account_asset_track.mt_asset_draft': lambda self, cr, uid,
                obj, ctx=None: obj.state == 'draft',
            'account_asset_track.mt_asset_open': lambda self, cr, uid,
                obj, ctx=None: obj.state == 'open',
            'account_asset_track.mt_asset_close': lambda self, cr, uid,
                obj, ctx=None: obj.state == 'close',
        },
    }
    
    name = fields.Char(track_visibility='onchange')
    code = fields.Char(track_visibility='onchange')
    category_id = fields.Many2one(track_visibility='onchange')
    purchase_date = fields.Date(track_visibility='onchange')
    name = fields.Char(track_visibility='onchange')