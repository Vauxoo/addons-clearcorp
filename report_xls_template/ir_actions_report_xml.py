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

from odoo import api, fields, models

REPORT_TYPES = [('qweb-xls', 'XLS'), ('qweb-ods', 'ODS')]


class ReportAction(models.Model):

    _inherit = 'ir.actions.report.xml'

    @api.model_cr
    def _lookup_report(self, name):
        """
        Look up a report definition.
        """
        self._cr.execute('SELECT * FROM ir_act_report_xml WHERE report_name=%s',(name,))
        r = self._cr.dictfetchone()
        if r:
            # Check if the report type fits with xls or ods reports
            if r['report_type'] in ['qweb-xls', 'qweb-ods']:
                # Return tuple (report name, report_type, module name)
                return (r['report_name'],
                        r['report_type'],
                        'report_xls_template')
        return super(ReportAction, self)._lookup_report(name)
    @api.model
    def render_report(self,res_ids, name, data):
        """
        Look up a report definition and render the report for the provided IDs.
        """
        new_report = self._lookup_report(name)

        if isinstance(new_report, tuple):  # Check the type of object
            # Check if the module is report_xls_template
            if new_report[2] == 'report_xls_template':
                # Check report type
                if new_report[1] == 'qweb-xls':
                    return self.env['report'].get_xls(res_ids, new_report[0],data=data), 'xls'
                elif new_report[1] == 'qweb-ods':
                    return self.env['report'].get_ods(res_ids, new_report[0], data=data), 'xls'
        return super(ReportAction, self).render_report(res_ids, name, data)

    report_type = fields.Selection(selection_add=REPORT_TYPES)
