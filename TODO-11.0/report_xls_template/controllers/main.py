# -*- coding: utf-8 -*-
# © 2014 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
# Code inspired by OpenERP SA report module

import json
from werkzeug import exceptions, url_decode
from odoo.http import Controller, route, request
from odoo.addons.web.controllers.main import _serialize_exception, content_disposition
from odoo.tools import html_escape


class ReportXLSController(Controller):

    @route([
        '/reportxlstemplate/<path:converter>/<reportname>',
        '/reportxlstemplate/<path:converter>/<reportname>/<docids>',
    ], type='http', auth='user', website=True)
    def report_routes(self, reportname, docids=None, converter=None, **data):
        report_obj = request.env['report']
        context = dict(request.env.context)

        if docids:
            docids = [int(i) for i in docids.split(',')]
        if data.get('options'):
            data.update(json.loads(data.pop('options')))
        if data.get('context'):
            # Ignore 'lang' here, because the context in data is the
            # one from the webclient *but* if the user explicitely
            # wants to change the lang, this mechanism overwrites it.
            data['context'] = json.loads(data['context'])
            if data['context'].get('lang'):
                del data['context']['lang']
            context.update(data['context'])

        if converter == 'xls':
            xls=report_obj.with_context(context).get_xls(docids, reportname, data=data)
            xlsxhttpheaders = [
                ('Content-Type',
                 'application/vnd.openxmlformats-officedocument.'
                 'spreadsheetml.sheet'),
                ('Content-Length', len(xls))]
            return request.make_response(xls, headers=xlsxhttpheaders)
        elif converter == 'ods':
            ods=report_obj.with_context(context).get_ods(docids, reportname, data=data)
            odshttpheaders = [
                ('Content-Type',
                 'application/vnd.oasis.opendocument.spreadsheet'),
                ('Content-Length', len(ods))]
            return request.make_response(ods, headers=odshttpheaders)
        else:
            raise exceptions.HTTPException(
                description='Converter %s not implemented.' % converter)

    @route(['/reportxlstemplate/download'], type='http', auth="user")
    def report_download(self, data, token):
        """This function is used by 'report_xls.js' in order to
        trigger the download of xls/ods report.
        :param token: token received by controller
        :param data: a javascript array JSON.stringified containg
        report internal url ([0]) and type [1]
        :returns: Response with a filetoken cookie and an attachment header
        """
        requestcontent = json.loads(data)
        url, report_type = requestcontent[0], requestcontent[1]
        try:
            if report_type == 'qweb-xls':
                reportname = url.split(
                    '/reportxlstemplate/xls/')[1].split('?')[0]
                docids = None
                if '/' in reportname:
                    reportname, docids = reportname.split('/')
                if docids:
                    # Generic report:
                    response = self.report_routes(reportname, docids=docids, converter='xls')
                else:
                    # Particular report:
                    # Decoding the args represented in JSON
                    data = url_decode(url.split('?')[1]).items()
                    response = self.report_routes(reportname, converter='xls', **dict(data))

                report = request.env['report']._get_xls_report_from_name(reportname)
                filename = "%s.%s" % (report.name, "xls")
                response.headers.add(
                    'Content-Disposition',
                    content_disposition(filename))
                response.set_cookie('fileToken', token)
                return response

            elif report_type == 'qweb-ods':
                reportname = url.split(
                    '/reportxlstemplate/ods/')[1].split('?')[0]
                docids = None
                if '/' in reportname:
                    reportname, docids = reportname.split('/')
                if docids:
                    # Generic report:
                    response = self.report_routes(reportname, docids=docids, converter='ods')
                else:
                    # Particular report:
                    # Decoding the args represented in JSON
                    data = url_decode(url.split('?')[1]).items()
                    response = self.report_routes(
                        reportname, converter='ods', **dict(data))


                report = request.env['report']._get_xls_report_from_name(reportname)
                filename = "%s.%s" % (report.name, "ods")
                response.headers.add(
                    'Content-Disposition',
                    content_disposition(filename))
                response.set_cookie('fileToken', token)
                return response

            else:
                return
        except Exception, e:
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return request.make_response(html_escape(json.dumps(error)))