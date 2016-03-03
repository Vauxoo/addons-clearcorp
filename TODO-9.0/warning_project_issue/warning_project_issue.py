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

from openerp import tools,models, fields, api,_
from openerp.tools.translate import _

WARNING_MESSAGE = [
                   ('no-message','No Message'),
                   ('warning','Warning'),
                   ('block','Blocking Message')
                   ]

WARNING_HELP = _('Selecting the "Warning" option will notify user with the message, Selecting "Blocking Message" will throw an exception with the message and block the flow. The Message has to be written in the next field.')

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    issue_warn = fields.Selection(WARNING_MESSAGE, 'Project Issue', help=WARNING_HELP, required=True)
    issue_warn_msg = fields.Text('Message for Issue')
    
    _defaults={
               'issue_warn': 'no-message'
               }

class project_issue(models.Model):
    _inherit = 'project.issue'
    @api.v7
    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        result = super(project_issue, self).onchange_partner_id(cr, uid, ids, partner_id,context=context)
        if not result.get('warning'):
            warning = {}
            title = False
            message = False
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
            if partner:
                if partner.parent_id:
                    if partner.parent_id.issue_warn != 'no-message':
                        title =  _("Warning for %s") % partner.name
                        message = partner.parent_id.issue_warn_msg
                        warning = {
                                   'title': title,
                                   'message': message,
                                   }
                        if partner.parent_id.issue_warn == 'block':
                            return {'value': {'partner_id': False}, 'warning': warning}
                        if result.get('warning',False):
                            warning['title'] = title and title +' & '+ result['warning']['title'] or result['warning']['title']
                            warning['message'] = message and message + ' ' + result['warning']['message'] or result['warning']['message']
                else:
                    if partner.issue_warn != 'no-message':
                        title =  _("Warning for %s") % partner.name
                        message = partner.issue_warn_msg
                        warning = {
                                   'title': title,
                                   'message': message,
                                   }
                        if partner.issue_warn == 'block':
                            return {'value': {'partner_id': False,'account_analytic_id':False},'domain':result['domain'],'warning': warning}
                        if result.get('warning',False):
                            warning['title'] = title and title +' & '+ result['warning']['title'] or result['warning']['title']
                            warning['message'] = message and message + ' ' + result['warning']['message'] or result['warning']['message']
                if warning:
                    result['warning'] = warning
        return result
