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

import base64
import StringIO
import csv
from openerp.osv import osv, fields
from openerp.tools.translate import _

class FeatureImportWizard(osv.TransientModel):
    
    _name = 'ccorp.project.oerp.feature.import.wizard'
    
    def import_file(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        try:
            file = StringIO.StringIO(base64.decodestring(wizard.file))
            reader = csv.reader(file, delimiter=';')
        except:
            raise osv.except_osv(_('Error'),_('An error occurred while reading the file. Please '
                                              'check if the format is correct.'))
        
        phase_obj = self.pool.get('project.phase')
        phase_ids = phase_obj.search(cr, uid, [('project_id','=',wizard.project_id.id)], context=context)
        work_type_obj = self.pool.get('ccorp.project.oerp.work.type')
        work_type_ids = work_type_obj.search(cr, uid, [('phase_id','in',phase_ids)], context=context)
        work_types = work_type_obj.browse(cr, uid, work_type_ids, context=context)
        
        # TODO: improve skip
        skipheader = True
        for row in reader:
            if skipheader:
                skipheader = False
                continue
            if row[2] == '':
                
                feature_type_id = self.pool.get('ccorp.project.scrum.feature.type').search(
                    cr, uid, [('code','=',row[0])], context=context) or False
                if feature_type_id: 
                    feature_type_id = feature_type_id[0]
                else: # TODO: log error
                    pass
                
                try:
                    values = {
                              'code': row[1],
                              'name': row[3],
                              'product_backlog_id': wizard.product_backlog_id.id,
                              'description': row[4],
                              'priority': int(row[5]),
                              'type_id': feature_type_id,
                              }
                    
                    hour_ids = []
                    for work_type in work_types:
                        try:
                            planned_hours = row[work_type.column_number-1]
                            if planned_hours == '':
                                planned_hours = 0.0
                            else:
                                planned_hours = float(planned_hours)
                            if planned_hours != 0.0:
                                vals = {
                                        'project_id': wizard.project_id.id,
                                        'phase_id': work_type.phase_id.id,
                                        'work_type_id': work_type.id,
                                        'expected_hours': planned_hours,
                                        }
                                hour_ids.append([0,False,vals])
                        except:
                            raise osv.except_osv(_('Error'),_('An error occurred while reading the planned hours '
                                'from file in column %s for work type %s') % (work_type.column_number, work_type.name))
                    values['hour_ids'] = hour_ids
                    
                    feature_obj = self.pool.get('ccorp.project.scrum.feature')
                    feature_obj.create(cr, uid, values, context=context)
                except Exception as error:
                    msg = _('An error occurred while importing the features. '
                            'The system error was :\n')
                    for item in error.args:
                        msg += item + '\n'
                    raise osv.except_osv(_('Error'), msg)
        return {
                'name': 'Features',
                'view_type': 'form',
                'view_mode': 'tree',
                'res_model': 'ccorp.project.scrum.feature',
                'context': context,
                'type': 'ir.actions.act_window',
                }
    
    _columns = {
                'project_id': fields.many2one('project.project', string='Project', required=True,
                    domain="[('is_scrum','=',True)]"),
                'product_backlog_id': fields.many2one('ccorp.project.scrum.product.backlog', string='Product Backlog',
                    required=True, domain="[('project_id','=',project_id)]"),
                'file': fields.binary('File to Import', required=True),
                'state': fields.selection([('new','New'),('done','Done')], string='State'),
                }
    
    _defaults = {
                 'state': 'new'
                 }