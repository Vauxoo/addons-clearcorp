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

from openerp.osv import osv, fields

class ResConfig(osv.TransientModel):

    _inherit = 'hr.config.settings'

    def onchange_attendance_company(self, cr, uid, ids, attendance_company_id, context=None):
        vals = {}
        if attendance_company_id:
            company_obj = self.pool.get('res.company')
            company= company_obj.browse(cr, uid, attendance_company_id, context=context)
            vals = {
                'attendance_date_format': company.attendance_date_format,
                'attendance_time_format': company.attendance_time_format,
                'attendance_sign_in': company.attendance_sign_in,
                'attendance_sign_out': company.attendance_sign_out,
                'attendance_normal_hours': company.attendance_normal_hours,
                'attendance_extra_hours': company.attendance_extra_hours,
                'attendance_default_sign_in': company.attendance_default_sign_in.id,
                'attendance_default_sign_out': company.attendance_default_sign_out.id,
                'attendance_importer_type':company.attendance_importer_type,
                'attendance_sample_template': company.attendance_sample_template
            }
        else:
            vals = {
                'attendance_date_format': False,
                'attendance_time_format':False,
                'attendance_sign_in': False,
                'attendance_sign_out': False,
                'attendance_normal_hours': False,
                'attendance_extra_hours': False,
                'attendance_default_sign_in': False,
                'attendance_default_sign_out': False,
                'attendance_importer_type':False,
                'attendance_sample_template': False
            }
        return {'value': vals}
    def onchange_attendance_importer_type(self, cr, uid, ids, attendance_importer_type, context=None):
        vals = {}
        if attendance_importer_type:
            if attendance_importer_type=='one_action_line':
                vals= {
                    'attendance_sample_filename': 'sample_template.csv',
                    'attendance_sample_template': 'RW1wbG95ZWUgQ29kZSxFbXBsb3llZSBOYW1lLERhdGUgYW5kIFRpbWUsQWN0aW9uLFdvcmsgSG91cgowMDEsRW1wbG95ZWUgT25lLDE1LzA1LzIwMTQgNjoxMDowMCxpbixOSAowMDIsRW1wbG95ZWUgVHdvLDE1LzA1LzIwMTQgNjowMDo1NSxpbixOSAowMDMsRW1wbG95ZWUgVGhyZWUsMTUvMDUvMjAxNCA1OjU1OjQ1LGluLE5ICjAwMSxFbXBsb3llZSBPbmUsMTUvMDUvMjAxNCAxNTowMjowMCxvdXQsTkgKMDAzLEVtcGxveWVlIFRocmVlLDE1LzA1LzIwMTQgMTU6MjI6MDAsb3V0LE5ICjAwMixFbXBsb3llZSBUd28sMTUvMDUvMjAxNCAxNDo1MDozMyxvdXQsTkgKMDAxLEVtcGxveWVlIE9uZSwxNS8wNS8yMDE0IDE1OjMyOjQ1LGluLEVICjAwMSxFbXBsb3llZSBPbmUsMTUvMDUvMjAxNCAxNzoyNzoyMixvdXQsRUgK',
                    }
            elif attendance_importer_type=='two_actions_line':
                vals= {
                    'attendance_sample_filename': 'sample_template.csv',
                    'attendance_sample_template': 'RW1wbG95ZWUgQ29kZSxFbXBsb3llZSBOYW1lLERhdGUsVGltZSBJbixUaW1lIE91dCxXb3JrIEhvdXIKMSxFbXBsb3llZSBPbmUsMTUvMDUvMjAxNCAsMDY6MTA6MDAsMTU6MDI6MDAsTkgKMixFbXBsb3llZSBUd28sMTUvMDUvMjAxNCAsMDY6MDA6NTUsMTQ6NTA6MzMsTkgKMyxFbXBsb3llZSBUaHJlZSwxNS8wNS8yMDE0LDA1OjU1OjQ1LDE1OjIyOjAwLE5ICjEsRW1wbG95ZWUgT25lLDE1LzA1LzIwMTQgLDE1OjMyOjQ1LDE3OjI3OjIyLEVICg==',
                    }
        
        return {'value': vals}
    
    def get_default_attendance_company_id(self, cr, uid, fields, context=None):
        """Get the default company for the module"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        return {'attendance_company_id': company_id}

    def get_default_attendance_date_format(self, cr, uid, fields, context=None):
        """Get the default company date_format"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_date_format': company.attendance_date_format}
    
    def get_default_attendance_time_format(self, cr, uid, fields, context=None):
        """Get the default company time_format"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_time_format': company.attendance_time_format}
    
    def set_attendance_date_format(self, cr, uid, ids, context=None):
        """Set the new attendance_date_format in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_date_format': config.attendance_date_format})
    
    def set_attendance_time_format(self, cr, uid, ids, context=None):
        """Set the new attendance_time_format in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_time_format': config.attendance_time_format})

    def get_default_attendance_sign_in(self, cr, uid, fields, context=None):
        """Get the default company sign in action"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_sign_in': company.attendance_sign_in}

    def set_attendance_sign_in(self, cr, uid, ids, context=None):
        """Set the new attendance_sign_in in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_sign_in': config.attendance_sign_in})

    def get_default_attendance_sign_out(self, cr, uid, fields, context=None):
        """Get the default company sign out action"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_sign_out': company.attendance_sign_out}

    def set_attendance_sign_out(self, cr, uid, ids, context=None):
        """Set the new attendance_sign_out in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_sign_out': config.attendance_sign_out})

    def get_default_attendance_normal_hours(self, cr, uid, fields, context=None):
        """Get the default company normal hours identifier"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_normal_hours': company.attendance_normal_hours}

    def set_attendance_normal_hours(self, cr, uid, ids, context=None):
        """Set the new attendance_normal_hours in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_normal_hours': config.attendance_normal_hours})

    def get_default_attendance_extra_hours(self, cr, uid, fields, context=None):
        """Get the default company extra hours identifier"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_extra_hours': company.attendance_extra_hours}

    def set_attendance_extra_hours(self, cr, uid, ids, context=None):
        """Set the new attendance_extra_hours in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_extra_hours': config.attendance_extra_hours})

    def get_default_attendance_default_sign_in(self, cr, uid, fields, context=None):
        """Get the default attendance_sign_in"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_default_sign_in': company.attendance_default_sign_in.id}

    def set_attendance_default_sign_in(self, cr, uid, ids, context=None):
        """Set the new attendance_default_sign_in in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_default_sign_in': config.attendance_default_sign_in.id})

    def get_default_attendance_default_sign_out(self, cr, uid, fields, context=None):
        """Get the default attendance_sign_out"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_default_sign_out': company.attendance_default_sign_out.id}

    def set_attendance_default_sign_out(self, cr, uid, ids, context=None):
        """Set the new attendance_default_sign_out in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_default_sign_out': config.attendance_default_sign_out.id})
    
    def get_default_attendance_importer_type(self, cr, uid, fields, context=None):
        """Get the default attendance_importer_type"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_importer_type': company.attendance_importer_type}

    def set_attendance_importer_type(self, cr, uid, ids, context=None):
        """Set the new attendance_importer_type in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_importer_type': config.attendance_importer_type})
        
    def get_default_attendance_sample_template(self, cr, uid, fields, context=None):
        """Get the attendance_sample_template"""
        company_obj = self.pool.get('res.company')
        company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
        company = company_obj.browse(cr, uid, company_id, context=context)
        return {'attendance_sample_template': company.attendance_sample_template}

    def set_attendance_sample_template(self, cr, uid, ids, context=None):
        """Set the new attendance_sample_template in the selected company"""
        config = self.browse(cr, uid, ids[0], context)
        config.attendance_company_id.write({'attendance_sample_template': config.attendance_sample_template})
    
    def get_default_attendance_sample_filename(self, cr, uid, ids,fields, context=None):
         """Get the default attendance_sample_template"""
         #company_obj = self.pool.get('res.company')
         #company_id = company_obj._company_default_get(cr, uid, 'hr.attendance.importer', context=context)
         #company = company_obj.browse(cr, uid, company_id, context=context)
         return {
                     'attendance_sample_filename': 'sample_template.csv',
                     }
    _columns = {
        'attendance_importer_type':fields.selection([('one_action_line','One action for line'),
            ('two_actions_line','Two actions for line (sign in and sign out actions)')],'Attendance importer type',
            required=True,help='Defines whether the import file, save one or two actions per line. ' 
            'If you select One action for line, each line will store a sign in or sign out action. '
            'If you select Two actions for line, each line will store a sign in and sign out action; '
            'In addition, the date field should be separated from the hours of sign in and sign out'),
        'attendance_company_id': fields.many2one('res.company', string='Company', required=True),
        'attendance_date_format': fields.char('Date format when importing files', size=32,
            help='Python date format used when importing files. For example '
            '07-31-2014 13:00:00 is %m-%d-Y %H:%M:%S'),
        'attendance_time_format': fields.char('Time format when importing files', size=32,
            help='Python time format used when importing files. For example '
            '13:00:00 is %H:%M:%S'),
        'attendance_sign_in': fields.char('Identifieone_action_liner for sign in actions', size=16,
            help='Used to identify sign-ins in the imported file. For example sign-in or IN.'),
        'attendance_sign_out': fields.char('Identifier for sign out actions', size=16,
            help='Used to identify sign-outs in the imported file. For example sign-out or OUT.'),
        'attendance_normal_hours': fields.char('Identifier for normal hours', size=8,
            help='Code used to identify normal hours in the imported file. For example NH.'),
        'attendance_extra_hours': fields.char('Identifier for extra hours', size=8,
            help='Code used to identify extra hours in the imported file. For example EH.'),
        'attendance_default_sign_in': fields.many2one('hr.action.reason', string='Default Sign in reason',
            help='Default action used to register extra hours sign-ins.'),
        'attendance_default_sign_out': fields.many2one('hr.action.reason', string='Default Sign out reason',
            help='Default action used to register extra hours sign-outs.'),
        'attendance_sample_template': fields.binary('Sample Template', readonly=True),
        'attendance_sample_filename': fields.char('Sample Template Filename', readonly=True),
    }
    _defaults={
               'attendance_importer_type':'one_action_line',
               }