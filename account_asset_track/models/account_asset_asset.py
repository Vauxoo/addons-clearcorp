# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, fields


class AccountAssetAsset(models.Model):
    _inherit = ['account.asset.asset', 'mail.thread']
    _name = 'account.asset.asset'

    _track = {
        'state': {
            'account_asset_track.mt_asset_draft':
                lambda self, cr, uid, obj, ctx=None: obj.state == 'draft',
            'account_asset_track.mt_asset_open':
                lambda self, cr, uid, obj, ctx=None: obj.state == 'open',
            'account_asset_track.mt_asset_close':
                lambda self, cr, uid, obj, ctx=None: obj.state == 'close',
        },
    }

    name = fields.Char(track_visibility='onchange')
    code = fields.Char(track_visibility='onchange')
    category_id = fields.Many2one(track_visibility='onchange')
    purchase_date = fields.Date(track_visibility='onchange')
