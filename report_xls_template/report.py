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

import xlwt
import lxml.html
import logging
import datetime
from StringIO import StringIO
from openerp import models, api, _
from openerp.exceptions import Warning

_logger = logging.getLogger('report_xls_template')


class Report(models.Model):

    _inherit = 'report'

    @api.v7
    def datetime_from_str(self, dt_str):
        """
        :returns: a datetime, if it matches the formats set
        """
        formats = [
            # <scope>, <pattern>, <format>
            ('day', 'YYYY-MM-DD', '%Y-%m-%d'),
            ('second', 'YYYY-MM-DD HH:MM:SS', '%Y-%m-%d %H:%M:%S'),
            ('microsecond', 'YYYY-MM-DD HH:MM:SS', '%Y-%m-%d %H:%M:%S'),
        ]
        for scope, pattern, format in formats:
            if scope == 'microsecond':
                if dt_str.count('.') != 1:
                    continue
                dt_str, microseconds_str = dt_str.split('.')
                try:
                    microsecond = int((microseconds_str + '000000')[:6])
                except ValueError:
                    continue
            try:
                t = datetime.datetime.strptime(dt_str, format)
            except ValueError:
                pass
            else:
                if scope == 'microsecond':
                    t = t.replace(microsecond=microsecond)
                return t
        else:
            raise ValueError

    @api.v7
    def get_html(self, cr, uid, ids, report_name, data=None, context=None):
        report = self._get_xls_report_from_name(cr, uid, report_name)
        if report:
            try:
                report_model_name = 'report.%s' % report_name
                particularreport_obj = self.pool[report_model_name]
                return particularreport_obj.render_html(
                    cr, uid, ids, data=data, context=context)
            except KeyError:
                report_obj = self.pool[report.model]
                docs = report_obj.browse(cr, uid, ids, context=context)
                docargs = {
                           'doc_ids': ids,
                           'doc_model': report.model,
                           'docs': docs,
                           }
                return self.pool.get('report').render(
                    cr, uid, [], report.report_name, docargs, context=context)
        else:
            return super(Report, self).get_html(
                cr, uid, ids, report_name, data=data, context=context)

    @api.v7
    def get_xls(self, cr, uid, ids, report_name,
                html=None, data=None, context=None):
        """
        This method generates and returns xls version of a report.
        """
        if context is None:
            context = {}

        report_obj = self.pool.get('report')
        if html is None:
            html = report_obj.get_html(
                cr, uid, ids, report_name, data=data, context=context)

        # Ensure the current document is utf-8 encoded.
        html = html.decode('utf-8')

        # Get the ir.actions.report.xml record we are working on.
        report = report_obj._get_xls_report_from_name(cr, uid, report_name)

        # Method should be rewriten for a more complex rendering
        def render_element_content(element):
            res = ''
            if isinstance(element.text, (str, unicode)):
                if element.tag == 'pre':
                    res += element.text
                else:
                    res += element.text.strip()
            for child in element:
                res += render_element_content(child)
            if isinstance(element.tail, (str, unicode)):
                res += element.tail.strip()
            return res

        # Method identify the data type
        def render_element_type(value):
            dt = ''
            try:
                dt = self.datetime_from_str(value)
                if dt or dt is not None:
                    return dt
            except:
                try:
                    return float(value)
                except:  # Not Float Type
                    return value

        # Create the workbook
        workbook = xlwt.Workbook()
        try:
            root = lxml.html.fromstring(html)
            # find the workbook div element
            div_workbook = root.xpath("//div[@class='workbook']")[0]
            # Find every worksheet on the report
            worksheet_counter = 1
            for div_worksheet in div_workbook.xpath(
                    "//div[@class='worksheet']"):
                # Add a worksheet with the desired name
                try:
                    if not xlwt.Utils.valid_sheet_name(div_worksheet.get(
                            'name', _('Data') + str(worksheet_counter))):
                        raise Warning(_('Invalid worksheet name.'))
                    worksheet = workbook.add_sheet(div_worksheet.get(
                            'name', _('Data') + str(worksheet_counter)))
                except (Warning, Exception) as exc:
                    raise Warning(exc.message)
                # Find all tables to add tho the worksheet
                row_index = 0
                for table in div_worksheet.xpath("table"):
                    # Write all headers to the worksheet
                    for header_row in table.xpath("thead/tr"):
                        column_index = 0
                        merged_rows = []
                        for column in header_row.xpath('th'):
                            style = None
                            try:
                                colspan_number = column.get('colspan', False)
                                rowspan_number = column.get('rowspan', False)

                                style_str = column.get('easyfx', False)
                                format_str = column.get(
                                    'num_format_str', False)
                                if style_str and format_str:
                                    style = xlwt.easyxf(
                                        style_str, num_format_str=format_str)
                                elif style_str and not format_str:
                                    style = xlwt.easyxf(style_str, None)
                                elif format_str and not style_str:
                                    style = xlwt.easyxf(
                                        '', num_format_str=format_str)
                            except:
                                _logger.info(
                                    'An error ocurred while loading the style')
                            if style:
                                worksheet.write(
                                    row_index, column_index,
                                    column.text, style)
                            else:
                                worksheet.write(
                                    row_index, column_index, column.text)
                            if colspan_number or rowspan_number:
                                try:
                                    colspan_number = colspan_number and \
                                        int(colspan_number)-1 or 0
                                    rowspan_number = rowspan_number and \
                                        int(rowspan_number)-1 or 0
                                    worksheet.merge(
                                        row_index, row_index +
                                        column_index + colspan_number)
                                    if colspan_number:
                                        column_index += colspan_number
                                    if rowspan_number:
                                        merged_rows.append(rowspan_number)
                                except:
                                    _logger.info(
                                        'An error ocurred while loading the'
                                        'style')
                            column_index += 1
                        row_index += merged_rows and max(merged_rows) + 1 or 1
                    # Write all content to the worksheet
                    for content_row in table.xpath("tbody/tr"):
                        column_index = 0
                        merged_rows = []
                        for column in content_row.xpath('td'):
                            style = None
                            try:
                                colspan_number = column.get('colspan', False)
                                rowspan_number = column.get('rowspan', False)
                                style_str = column.get('easyfx', False)
                                format_str = column.get(
                                    'num_format_str', False)
                                if style_str and format_str:
                                    style = xlwt.easyxf(
                                        style_str,
                                        num_format_str=format_str)
                                elif style_str and not format_str:
                                    style = xlwt.easyxf(style_str, None)
                                elif format_str and not style_str:
                                    style = xlwt.easyxf(
                                        '', num_format_str=format_str)
                            except:
                                _logger.info(
                                    'An error ocurred while loading the style')
                            if style:
                                worksheet.write(
                                    row_index, column_index,
                                    render_element_type(
                                        render_element_content(column)), style)
                            else:
                                worksheet.write(
                                    row_index, column_index,
                                    render_element_type(
                                        render_element_content(column)))
                            if colspan_number or rowspan_number:
                                try:
                                    colspan_number = colspan_number and \
                                        int(colspan_number)-1 or 0
                                    rowspan_number = rowspan_number and \
                                        int(rowspan_number)-1 or 0
                                    worksheet.merge(
                                        row_index, row_index +
                                        rowspan_number, column_index,
                                        column_index + colspan_number)
                                    if colspan_number:
                                        column_index += colspan_number
                                    if rowspan_number:
                                        merged_rows.append(rowspan_number)
                                except:
                                    _logger.info(
                                        'An error ocurred while '
                                        'loading the style')
                            column_index += 1
                        row_index += merged_rows and max(merged_rows) + 1 or 1
                worksheet_counter += 1
        except:
            raise Warning(
                _('An error occurred while parsing the view into file.'))

        output = StringIO()
        workbook.save(output)  # Save the workbook that we are going to return
        output.seek(0)
        return output.read()

    @api.v8
    def get_xls(self, records, report_name, html=None, data=None):
        return self._model.get_xls(
            self._cr, self._uid, records.ids, report_name,
            html=html, data=data, context=self._context)

    @api.v7
    def get_ods(
            self, cr, uid, ids, report_name,
            html=None, data=None, context=None):
        raise NotImplementedError

    @api.v8
    def get_ods(self, records, report_name, html=None, data=None):
        raise NotImplementedError

    def _get_xls_report_from_name(self, cr, uid, report_name):
        """
        Get the first record of ir.actions.report.xml having
        the ``report_name`` as value for the field report_name.
        """
        report_obj = self.pool['ir.actions.report.xml']
        qweb_xls_types = ['qweb-xls', 'qweb-ods']
        conditions = [
            ('report_type', 'in', qweb_xls_types),
            ('report_name', '=', report_name)]
        idreport = report_obj.search(cr, uid, conditions)
        if idreport:
            return report_obj.browse(cr, uid, idreport[0])
        return None
