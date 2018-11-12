# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = 'res.company'
    _order = 'prefix'

    prefix = fields.Char('Prefix', size=10, default='')

    @api.multi
    def name_get(self):
        res = []
        for obj_company in self:
            obj_company_name = obj_company.prefix and obj_company.prefix + \
                ' ' or ''
            obj_company_name += obj_company.name
            res.append((obj_company.id, obj_company_name))
        return res
