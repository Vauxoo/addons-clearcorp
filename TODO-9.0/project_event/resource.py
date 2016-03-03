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

from openerp import models, fields, api

class Resource(models.Model):

    _name= 'project.event.resource'
    _inherits = {'resource.resource': 'resource_id'}

    @api.onchange('resource_type')
    def onchange_resource_type(self):
        self.unlimited = False

    @api.multi
    def name_get(self):
        result = []
        for resource in self:
            if resource.code:
                result.append((resource.id, "[%s] - %s" % (resource.code, resource.name or '')))
            else:
                result.append((resource.id, "%s" % resource.name or ''))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search([('code', operator, name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()

    unlimited = fields.Boolean('Unlimited', help='This resource is able to '
        'be scheduled in many events at the same time')
    category_id = fields.Many2one('project.event.resource.category', string='Category')
    resource_id = fields.Many2one('resource.resource', string='Resource',
        ondelete='cascade', required=True)