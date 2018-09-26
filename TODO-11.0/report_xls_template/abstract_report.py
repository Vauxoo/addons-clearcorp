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

from odoo import api, models


class AbstractReport(models.AbstractModel):
    """Model used to embed old style reports"""

    _inherit = 'report.abstract_report'
    _report_render_type = None
    @api.model
    def render_html(self,ids, data=None):

        if self._report_render_type == 'qweb-xls':
            context = dict(self.env.context or {})

            if context and context.get('active_ids'):
                # Browse the selected objects via their reference in context
                model = context.get('active_model') or context.get('model')
                objects_model = self.env[model]
                objects = objects_model.with_context(context).browse(context['active_ids'])
            else:
                # If no context is set (for instance,
                # during test execution), build one
                model = self.env['report']._get_xls_report_from_name(self._template).model
                objects_model = self.env[model]
                objects = objects_model.with_context(context).browse(ids)
                context['active_model'] = model
                context['active_ids'] = ids

            # Generate the old style report
            wrapped_report = self.with_context(context)._wrapped_report_class(self.env.cr, self.env.uid, '', context=self.env.context)
            wrapped_report.set_context(objects, data, context['active_ids'])

            # Rendering self._template with the wrapped
            # report instance localcontext as
            # rendering environment
            docargs = dict(wrapped_report.localcontext)
            if not docargs.get('lang'):
                docargs.pop('lang', False)
            docargs['docs'] = docargs.get('objects')

            # Used in template translation (see
            # translate_doc method from report model)
            docargs['doc_ids'] = context['active_ids']
            docargs['doc_model'] = model

            return self.env['report'].with_context(context).render(self._template, docargs)
        else:
            return super(AbstractReport, self).render_html(ids, data=data)
