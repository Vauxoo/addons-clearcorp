# -*- coding: utf-8 -*-
# © 2014 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import ast
import xlsxwriter
import lxml.html
import logging
import base64
import datetime
from io import BytesIO
from cStringIO import StringIO
from openerp import models, api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.exceptions import Warning


DEFAULT_DATE_FORMAT = 'm/d/yyyy'
DEFAULT_DATETIME_FORMAT = 'm/d/yyyy h:mm'
DEFAULT_INTEGER_FORMAT = '0'
DEFAULT_FLOAT_FORMAT = '0.00'

_logger = logging.getLogger('report_xls_template')


class Report(models.Model):

    _inherit = 'report'

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

        def render_element_value(value, type):
            if type == 'date':
                return datetime.datetime.strptime(
                    value, DEFAULT_SERVER_DATE_FORMAT).date()
            if type == 'datetime':
                return datetime.datetime.strptime(
                    value, DEFAULT_SERVER_DATETIME_FORMAT)
            try:
                val = ast.literal_eval(value)
                return val
            except Exception as e:
                _logger.info(
                    'Could not convert %s to type.' % e.message)
            return value

        # Method should be rewritten for a more complex rendering
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

        def get_default_format(value):
            if isinstance(value, datetime.datetime):
                return DEFAULT_DATETIME_FORMAT
            if isinstance(value, datetime.date):
                return DEFAULT_DATE_FORMAT
            if isinstance(value, int):
                return DEFAULT_INTEGER_FORMAT
            if isinstance(value, float):
                return DEFAULT_FLOAT_FORMAT
            return 'General'

        def insert_image(worksheet, image, row_index, column_index):
            src = image.get('src', False)
            x_scale = float(image.get('x_scale', False)) or 1
            y_scale = float(image.get('y_scale', False)) or 1
            x_offset = float(image.get('x_offset', False)) or 0
            y_offset = float(image.get('y_offset', False)) or 0
            tip = image.get('tip', None)
            if not src:
                return
            src = src.replace('data:image/png;base64,', '')
            img = StringIO()
            img.write(base64.decodestring(src))
            img.seek(0)
            image_data = BytesIO(img.read())
            img.close()
            worksheet.insert_image(row_index, column_index, 'image.png', {
                'x_scale': x_scale,
                'y_scale': y_scale,
                'x_offset': x_offset,
                'y_offset': y_offset,
                'tip': tip,
                'image_data': image_data,
            })

        def write_cell(
                worksheet, column, row_index,
                column_index, rowspan_number, colspan_number):

            type = column.get("type", None)
            value = render_element_content(column)
            value = render_element_value(value, type)

            # Compute format
            cell_format = column.get('format', False)
            try:
                if cell_format:
                    cell_format = ast.literal_eval(cell_format)
                    if 'num_format' not in cell_format.keys():
                        cell_format['num_format'] = get_default_format(value)
                else:
                    # Set default format if not format is available
                    cell_format = {'num_format': get_default_format(value)}
                cell_format = workbook.add_format(cell_format)
            except Exception as exc:
                cell_format = False
                _logger.info(
                    'An error occurred loading the format. %s' % exc.message)

            if colspan_number or rowspan_number:
                try:
                    colspan_number = colspan_number and \
                        (colspan_number - 1) or 0
                    rowspan_number = rowspan_number and \
                        (rowspan_number - 1) or 0
                    worksheet.merge_range(
                        row_index, column_index, row_index + rowspan_number,
                        column_index + colspan_number, value, cell_format)
                except Exception:
                    _logger.info(
                        'An error occurred while merging cells')
            else:
                worksheet.write(row_index, column_index, value, cell_format)
            try:
                # Insert all images
                for image in column.xpath('img'):
                    insert_image(worksheet, image, row_index, column_index)
            except:
                _logger.info('An error occurred inserting images.')

        # Create the workbook
        output = StringIO()
        workbook = xlsxwriter.Workbook(output)
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
                    name = div_worksheet.get('name', False)
                    worksheet = workbook.add_worksheet(name)
                except (Warning, Exception) as exc:
                    raise Warning(exc.message)
                # Set number of pages and orientation
                orientation = div_worksheet.get('orientation', False)
                fithorizontal = div_worksheet.get('fithorizontal', 0)
                fitvertical = div_worksheet.get('fitvertical', 0)
                # No need to set it if portrait
                if orientation and orientation == 'landscape':
                    worksheet.set_landscape()
                if fithorizontal and fitvertical:
                    worksheet.fit_to_pages(fithorizontal, fitvertical)
                else:
                    if fithorizontal or fitvertical:
                        worksheet.fit_to_pages(fithorizontal, fitvertical)

                # Find all tables to add tho the worksheet
                row_index = 0
                for table in div_worksheet.xpath("table"):
                    # Write all headers to the worksheet
                    for header_row in table.xpath("thead/tr"):
                        column_index = 0
                        merged_rows = []
                        rowheight = header_row.get('rowheight', False)
                        if rowheight:
                            worksheet.set_row(row_index, float(rowheight))
                        for column in header_row.xpath('th'):
                            colwidth = column.get('colwidth', False)
                            colspan_number = int(column.get('colspan', False))
                            rowspan_number = int(column.get('rowspan', False))
                            if colwidth:
                                worksheet.set_column(
                                    row_index, column_index, float(colwidth))
                            write_cell(
                                worksheet, column, row_index,
                                column_index, rowspan_number, colspan_number)
                            if colspan_number:
                                column_index += (colspan_number - 1)
                            if rowspan_number:
                                merged_rows.append(rowspan_number)
                            column_index += 1
                        row_index += merged_rows and max(merged_rows) or 1
                    # Write all content to the worksheet
                    for content_row in table.xpath("tbody/tr"):
                        column_index = 0
                        merged_rows = []
                        rowheight = content_row.get('rowheight', False)
                        if rowheight:
                            worksheet.set_row(row_index, float(rowheight))
                        for column in content_row.xpath('td'):
                            colwidth = column.get('colwidth', False)
                            colspan_number = int(column.get('colspan', False))
                            rowspan_number = int(column.get('rowspan', False))
                            if colwidth:
                                worksheet.set_column(
                                    row_index, column_index, float(colwidth))
                            write_cell(
                                worksheet, column, row_index,
                                column_index, rowspan_number, colspan_number)
                            if colspan_number:
                                column_index += (colspan_number - 1)
                            if rowspan_number:
                                merged_rows.append(rowspan_number)
                            column_index += 1
                        row_index += merged_rows and max(merged_rows) or 1
                worksheet_counter += 1
        except:
            raise Warning(
                _('An error occurred while parsing the view into file.'))

        workbook.close()  # Save the workbook that we are going to return
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
