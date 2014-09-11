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

import csv
import pytz
import base64
import StringIO
from datetime import datetime
from openerp.osv import osv, fields
from openerp.tools.translate import _

STATES = [('invalid','Invalid'),('valid','Valid')]

class ActionReason(osv.TransientModel):

    _name = 'hr.attendance.importer.action.reason'

    _columns = {
        'name': fields.char('Action Reason', size=64, required=True, readonly=True),
        'action_type': fields.selection([('sign_in','Sign In'),('sign_out','Sign Out')], string='Action Type', required=True),
        'wizard_id': fields.many2one('hr.attendance.importer.file.import.wizard', 'Wizard', ondelete='cascade', readonly=True),
    }

    _defaults = {
        'action_type': 'sign_in',
    }

class Attendance(osv.TransientModel):

    _name = 'hr.attendance.importer.attendance'

    _order = 'name asc'

    def _compute_state(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        attendance_obj = self.pool.get('hr.attendance')
        for attendance in self.browse(cr, uid, ids, context=context):
            #valid = False
            # Check type of action
            if attendance.action == 'action':
                if not attendance.action_desc:
                    res[attendance.id] = 'invalid'
                    continue
                action = attendance.action_desc.action_type
                attendance_db = False
                attendance_mem = False
                cond = [('employee_id','=',attendance.employee_id.id),
                        ('name','<',attendance.name),
                        ('id','!=',attendance.id)]
                # Query for db items
                attendance_ids = attendance_obj.search(cr, uid, cond, order='name desc', limit=1, context=context)
                if attendance_ids:
                    attendance_db = attendance_obj.browse(cr, uid, attendance_ids[0], context=context)
                # Query for memory items
                cond.append(('wizard_id','=',attendance.wizard_id.id))
                attendance_ids = self.search(cr, uid, cond, order='name desc', limit=1, context=context)
                if attendance_ids:
                    attendance_mem = self.browse(cr, uid, attendance_ids[0], context=context)
                if action == 'sign_in':
                    # Set as valid because it is the first register
                    if not attendance_db and not attendance_mem:
                        res[attendance.id] = 'valid'
                        continue
                    # There are no register on db
                    elif not attendance_db:
                        if attendance_mem.action == 'action':
                            if attendance_mem.action_desc:
                                if attendance_mem.action_desc.action_type == 'sign_out':
                                    res[attendance.id] = 'valid'
                                    continue
                                else:
                                    res[attendance.id] = 'invalid'
                                    continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                        elif attendance_mem.action == 'sign_out':
                            res[attendance.id] = 'valid'
                            continue
                        else:
                            res[attendance.id] = 'invalid'
                            continue
                    # There are no registers on memory
                    elif not attendance_mem:
                        if attendance_db.action == 'action':
                            if attendance_db.action_desc:
                                if attendance_db.action_desc.action_type == 'sign_out':
                                    res[attendance.id] = 'valid'
                                    continue
                                else:
                                    res[attendance.id] = 'invalid'
                                    continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                        elif attendance_db.action == 'sign_out':
                            res[attendance.id] = 'valid'
                            continue
                        else:
                            res[attendance.id] = 'invalid'
                            continue
                    # Both are available
                    else:
                        # Mem item is closer than  db item
                        if datetime.strptime(attendance_db.name,'%Y-%m-%d %H:%M:%S') < datetime.strptime(attendance_mem.name,'%Y-%m-%d %H:%M:%S'):
                            if attendance_mem.state == 'invalid':
                                res[attendance.id] = 'invalid'
                                continue
                            if attendance_mem.action == 'action':
                                if attendance_mem.action_desc:
                                    if attendance_mem.action_desc.action_type == 'sign_out':
                                        res[attendance.id] = 'valid'
                                        continue
                                    else:
                                        res[attendance.id] = 'invalid'
                                        continue
                                else:
                                    res[attendance.id] = 'invalid'
                                    continue
                            elif attendance_mem.action == 'sign_out':
                                res[attendance.id] = 'valid'
                                continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                        # Db item is closer than mem item
                        else:
                            if attendance_db.action == 'action':
                                if attendance_db.action_desc:
                                    if attendance_db.action_desc.action_type == 'sign_out':
                                        res[attendance.id] = 'valid'
                                        continue
                                    else:
                                        res[attendance.id] = 'invalid'
                                        continue
                                else:
                                    res[attendance.id] = 'invalid'
                                    continue
                            elif attendance_db.action == 'sign_out':
                                res[attendance.id] = 'valid'
                                continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                else:
                    # Set as invalid because it is the first register
                    if not attendance_db and not attendance_mem:
                        res[attendance.id] = 'invalid'
                        continue
                    # There are no register on db
                    elif not attendance_db:
                        if attendance_mem.action == 'action':
                            if attendance_mem.action_desc:
                                if attendance_mem.action_desc.action_type == 'sign_in':
                                    res[attendance.id] = 'valid'
                                    continue
                                else:
                                    res[attendance.id] = 'invalid'
                                    continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                        elif attendance_mem.action == 'sign_in':
                            res[attendance.id] = 'valid'
                            continue
                        else:
                            res[attendance.id] = 'invalid'
                            continue
                    # There are no registers on memory
                    elif not attendance_mem:
                        if attendance_db.action == 'action':
                            if attendance_db.action_desc:
                                if attendance_db.action_desc.action_type == 'sign_in':
                                    res[attendance.id] = 'valid'
                                    continue
                                else:
                                    res[attendance.id] = 'invalid'
                                    continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                        elif attendance_db.action == 'sign_in':
                            res[attendance.id] = 'valid'
                            continue
                        else:
                            res[attendance.id] = 'invalid'
                            continue
                    # Both are available
                    else:
                        # Mem item is closer than  db item
                        if datetime.strptime(attendance_db.name,'%Y-%m-%d %H:%M:%S') < datetime.strptime(attendance_mem.name,'%Y-%m-%d %H:%M:%S'):
                            if attendance_mem.state == 'invalid':
                                res[attendance.id] = 'invalid'
                                continue
                            if attendance_mem.action == 'action':
                                if attendance_mem.action_desc:
                                    if attendance_mem.action_desc.action_type == 'sign_in':
                                        res[attendance.id] = 'valid'
                                        continue
                                    else:
                                        res[attendance.id] = 'invalid'
                                        continue
                                else:
                                    res[attendance.id] = 'invalid'
                                    continue
                            elif attendance_mem.action == 'sign_in':
                                res[attendance.id] = 'valid'
                                continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                        # Db item is closer than mem item
                        else:
                            if attendance_db.action == 'action':
                                if attendance_db.action_desc:
                                    if attendance_db.action_desc.action_type == 'sign_in':
                                        res[attendance.id] = 'valid'
                                        continue
                                    else:
                                        res[attendance.id] = 'invalid'
                                        continue
                                else:
                                    res[attendance.id] = 'invalid'
                                    continue
                            elif attendance_db.action == 'sign_in':
                                res[attendance.id] = 'valid'
                                continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
            # Check type of sign_in
            elif attendance.action == 'sign_in':
                attendance_db = False
                attendance_mem = False
                cond = [('employee_id','=',attendance.employee_id.id),
                        ('name','<',attendance.name),
                        ('id','!=',attendance.id)]
                # Query for db items
                attendance_ids = attendance_obj.search(cr, uid, cond, order='name desc', limit=1, context=context)
                if attendance_ids:
                    attendance_db = attendance_obj.browse(cr, uid, attendance_ids[0], context=context)
                # Query for memory items
                cond.append(('wizard_id','=',attendance.wizard_id.id))
                attendance_ids = self.search(cr, uid, cond, order='name desc', limit=1, context=context)
                if attendance_ids:
                    attendance_mem = self.browse(cr, uid, attendance_ids[0], context=context)
                    print attendance.id
                    print attendance.name, attendance.employee_id.name, attendance.action
                    print attendance_mem.id
                    print attendance_mem.name, attendance_mem.employee_id.name, attendance_mem.action
                # Set as valid because it is the first register
                if not attendance_db and not attendance_mem:
                    res[attendance.id] = 'valid'
                    continue
                # There are no register on db
                elif not attendance_db:
                    if attendance_mem.action == 'action':
                        if attendance_mem.action_desc:
                            if attendance_mem.action_desc.action_type == 'sign_out':
                                res[attendance.id] = 'valid'
                                continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                        else:
                            res[attendance.id] = 'invalid'
                            continue
                    elif attendance_mem.action == 'sign_out':
                        res[attendance.id] = 'valid'
                        continue
                    else:
                        res[attendance.id] = 'invalid'
                        continue
                # There are no registers on memory
                elif not attendance_mem:
                    if attendance_db.action == 'action':
                        if attendance_db.action_desc:
                            if attendance_db.action_desc.action_type == 'sign_out':
                                res[attendance.id] = 'valid'
                                continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                        else:
                            res[attendance.id] = 'invalid'
                            continue
                    elif attendance_db.action == 'sign_out':
                        res[attendance.id] = 'valid'
                        continue
                    else:
                        res[attendance.id] = 'invalid'
                        continue
                # Both are available
                else:
                    # Mem item is closer than  db item
                    if datetime.strptime(attendance_db.name,'%Y-%m-%d %H:%M:%S') < datetime.strptime(attendance_mem.name,'%Y-%m-%d %H:%M:%S'):
                        if attendance_mem.state == 'invalid':
                            res[attendance.id] = 'invalid'
                            continue
                        if attendance_mem.action == 'action':
                            if attendance_mem.action_desc:
                                if attendance_mem.action_desc.action_type == 'sign_out':
                                    res[attendance.id] = 'valid'
                                    continue
                                else:
                                    res[attendance.id] = 'invalid'
                                    continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                        elif attendance_mem.action == 'sign_out':
                            res[attendance.id] = 'valid'
                            continue
                        else:
                            res[attendance.id] = 'invalid'
                            continue
                    # Db item is closer than mem item
                    else:
                        if attendance_db.action == 'action':
                            if attendance_db.action_desc:
                                if attendance_db.action_desc.action_type == 'sign_out':
                                    res[attendance.id] = 'valid'
                                    continue
                                else:
                                    res[attendance.id] = 'invalid'
                                    continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                        elif attendance_db.action == 'sign_out':
                            res[attendance.id] = 'valid'
                            continue
                        else:
                            res[attendance.id] = 'invalid'
                            continue
            #Check type of sign_out
            else:
                attendance_db = False
                attendance_mem = False
                cond = [('employee_id','=',attendance.employee_id.id),
                        ('name','<',attendance.name),
                        ('id','!=',attendance.id)]
                # Query for db items
                attendance_ids = attendance_obj.search(cr, uid, cond, order='name desc', limit=1, context=context)
                if attendance_ids:
                    attendance_db = attendance_obj.browse(cr, uid, attendance_ids[0], context=context)
                # Query for memory items
                cond.append(('wizard_id','=',attendance.wizard_id.id))
                attendance_ids = self.search(cr, uid, cond, order='name desc', limit=1, context=context)
                if attendance_ids:
                    attendance_mem = self.browse(cr, uid, attendance_ids[0], context=context)
                # Set as invalid because it is the first register
                if not attendance_db and not attendance_mem:
                    res[attendance.id] = 'invalid'
                    continue
                # There are no register on db
                elif not attendance_db:
                    if attendance_mem.action == 'action':
                        if attendance_mem.action_desc:
                            if attendance_mem.action_desc.action_type == 'sign_in':
                                res[attendance.id] = 'valid'
                                continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                        else:
                            res[attendance.id] = 'invalid'
                            continue
                    elif attendance_mem.action == 'sign_in':
                        res[attendance.id] = 'valid'
                        continue
                    else:
                        res[attendance.id] = 'invalid'
                        continue
                # There are no registers on memory
                elif not attendance_mem:
                    if attendance_db.action == 'action':
                        if attendance_db.action_desc:
                            if attendance_db.action_desc.action_type == 'sign_in':
                                res[attendance.id] = 'valid'
                                continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                        else:
                            res[attendance.id] = 'invalid'
                            continue
                    elif attendance_db.action == 'sign_in':
                        res[attendance.id] = 'valid'
                        continue
                    else:
                        res[attendance.id] = 'invalid'
                        continue
                # Both are available
                else:
                    # Mem item is closer than  db item
                    if datetime.strptime(attendance_db.name,'%Y-%m-%d %H:%M:%S') < datetime.strptime(attendance_mem.name,'%Y-%m-%d %H:%M:%S'):
                        if attendance_mem.state == 'invalid':
                            res[attendance.id] = 'invalid'
                            continue
                        if attendance_mem.action == 'action':
                            if attendance_mem.action_desc:
                                if attendance_mem.action_desc.action_type == 'sign_in':
                                    res[attendance.id] = 'valid'
                                    continue
                                else:
                                    res[attendance.id] = 'invalid'
                                    continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                        elif attendance_mem.action == 'sign_in':
                            res[attendance.id] = 'valid'
                            continue
                        else:
                            res[attendance.id] = 'invalid'
                            continue
                    # Db item is closer than mem item
                    else:
                        if attendance_db.action == 'action':
                            if attendance_db.action_desc:
                                if attendance_db.action_desc.action_type == 'sign_in':
                                    res[attendance.id] = 'valid'
                                    continue
                                else:
                                    res[attendance.id] = 'invalid'
                                    continue
                            else:
                                res[attendance.id] = 'invalid'
                                continue
                        elif attendance_db.action == 'sign_in':
                            res[attendance.id] = 'valid'
                            continue
                        else:
                            res[attendance.id] = 'invalid'
                            continue
        return res

    _columns = {
        'employee_id': fields.many2one('hr.employee', string='Employee', required=True),
        'name': fields.datetime('Date', required=True),
        'action': fields.selection([('sign_in','Sign In'),('sign_out','Sign Out'),('action',('Action'))], string='Action', required=True),
        'action_desc': fields.many2one('hr.attendance.importer.action.reason', 'Action Reason'),
        'wizard_id': fields.many2one('hr.attendance.importer.file.import.wizard', 'Wizard', ondelete='cascade'),
        'state': fields.function(_compute_state, type='selection', selection=STATES, string='State'),
    }

class FileImportWizard(osv.TransientModel):

    _name = 'hr.attendance.importer.file.import.wizard'

    def onchange_user(self, cr, uid, ids, user_id, context=None):
        vals = {}
        if user_id:
            user = self.pool.get('res.users').browse(cr, uid, user_id, context=context)
            vals['tz'] = user.tz
            print user.tz
        else:
            vals['tz'] = ''
        return {'value': vals}

    def import_file(self, cr, uid, ids, context=None):
        result = ''
        wizard = self.browse(cr, uid, ids[0], context=context)
        # Validate required parameter to run wizard
        if not wizard.company_id.attendance_normal_hours or not wizard.company_id.attendance_extra_hours:
            raise osv.except_osv(_('Error'), _('An error occurred while reading the file. There is not an '
                'hour identifier defined for attendance files on company %s') % (wizard.company_id.name))
        if not wizard.company_id.attendance_sign_in or not wizard.company_id.attendance_sign_out:
            raise osv.except_osv(_('Error'), _('An error occurred while reading the file. There is '
                'not a sign in or sign out defined for attendance files on company %s') % (wizard.company_id.name))
        if not wizard.company_id.attendance_date_format:
            raise osv.except_osv(_('Error'), _('An error occurred while reading the file. There is not a '
                'date format defined for attendance files on company %s') % (wizard.company_id.name))
        # Read the file
        try:
            file = StringIO.StringIO(base64.decodestring(wizard.file))
            reader = csv.reader(file, delimiter=',')
        except:
            raise osv.except_osv(_('Error'),_('An error occurred while reading the file. Please '
                                              'check if the format is correct.'))
        # Iterate over the cvs reader to review items and create
        # all the necesary objects
        skip_header = True
        line_number = 1
        invalid_ids = []
        valid_ids = []
        for row in reader:
            if skip_header:
                skip_header = False
                continue
            employee_code = row[0]
            employee_name = row[1]
            date = datetime.strptime(row[2], wizard.company_id.attendance_date_format)
            if wizard.tz:
                utc = pytz.timezone('UTC')
                timezone = pytz.timezone(wizard.tz)
                date = timezone.localize(date, is_dst=False) # UTC = no DST
                date = date.astimezone(utc)
            date = datetime.strftime(date,'%Y-%m-%d %H:%M:%S')
            
            action = row[3]
            hour_type = row[4]
            employee_obj = self.pool.get('hr.employee')
            employee_id = employee_obj.search(cr, uid, [('code','=',employee_code)], context=context)
            # Add errors to result in order to proceed to check out wrong data
            if not employee_id:
                result += _('Error in line %d: Employee %s with code %s was not '
                            'found.\n') % (line_number, employee_name, employee_code)
                line_number += 1
                continue
            if hour_type == wizard.company_id.attendance_normal_hours:
                vals = {
                    'employee_id': employee_id[0],
                    'name': date,
                    'action': False,
                    'action_desc': False,
                    'wizard_id': wizard.id,
                }
                if action == wizard.company_id.attendance_sign_in:
                    vals['action'] = 'sign_in'
                elif action == wizard.company_id.attendance_sign_out:
                    vals['action'] = 'sign_out'
                else:
                    result += _('Error in line %d: Wrong action %s\n') % (line_number, action)
                    line_number += 1
                    continue
                self.pool.get('hr.attendance.importer.attendance').create(cr, uid, vals, context=context)
            elif hour_type == wizard.company_id.attendance_extra_hours:
                action_vals = {'name':_('Imported Extra Hours'), 'action_type': False, 'wizard_id': wizard.id}
                if action == wizard.company_id.attendance_sign_in:
                    action_vals['action_type'] = 'sign_in'
                elif action == wizard.company_id.attendance_sign_out:
                    action_vals['action_type'] = 'sign_out'
                else:
                    result += _('Error in line %d: Wrong action %s\n') % (line_number, action)
                    line_number += 1
                    continue
                action_desc_id = self.pool.get('hr.attendance.importer.action.reason').create(cr, uid, action_vals, context=context)
                vals = {
                    'employee_id': employee_id[0],
                    'name': date,
                    'action': 'action',
                    'action_desc': action_desc_id,
                    'wizard_id': wizard.id,
                }
                self.pool.get('hr.attendance.importer.attendance').create(cr, uid, vals, context=context)
            else:
                result += _('Error in line %d: Invalid hour type %s\n') % (line_number, hour_type)
                line_number += 1
                continue
            line_number += 1
        if result == '':
            result = _('There were no errors found for this file.')
        wizard.write({'state': 'error', 'result': result}, context=context)
        return {
                'name': _('View Errors'),
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': context,
                'res_id': wizard.id,
                }

    def view_items(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        wizard.write({'state': 'view'}, context=context)
        return {
                'name': _('View Items'),
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'context': context,
                'res_id': wizard.id,
                }

    def done(self, cr, uid, ids, context=None):
        wizard = self.browse(cr, uid, ids[0], context=context)
        new_ids = []
        if not wizard.company_id.attendance_default_sign_in or not wizard.company_id.attendance_default_sign_out:
            raise osv.except_osv(_('Error'), _('An error occurred while reading the file. There is not a '
                'default sign in/out defined for attendance files on company %s') % (wizard.company_id.name))
        for attendance in wizard.attendance_ids:
            try:
                if attendance.action == 'action':
                    action_reason_obj = self.pool.get('hr.action.reason')
                    attendance_obj = self.pool.get('hr.attendance')
                    if attendance.action_desc.action_type == 'sign_in':
                        action_id = wizard.company_id.attendance_default_sign_in.id
                    else:
                        action_id = wizard.company_id.attendance_default_sign_out.id
                    values = {
                        'employee_id': attendance.employee_id.id,
                        'name': attendance.name,
                        'action': attendance.action,
                        'action_desc': action_id,
                    }
                    elem = attendance_obj.create(cr, uid, values, context=context)
                    new_ids.append(elem)
                else:
                    attendance_obj = self.pool.get('hr.attendance')
                    values = {
                        'employee_id': attendance.employee_id.id,
                        'name': attendance.name,
                        'action': attendance.action,
                    }
                    elem = attendance_obj.create(cr, uid, values, context=context)
                    new_ids.append(elem)
            except Exception as error:
                msg = _('An error occurred while importing the assistance for %s '
                        'on date and time %s. Please go back and check the item.\n'
                        'The system error was :\n') % (attendance.employee_id.name,
                        attendance.name)
                for item in error.args:
                    msg += item + '\n'
                raise osv.except_osv(_('Error'), msg)
        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'hr_attendance', 'view_attendance_who')
        return {
                'name': _('Recently Created Items'),
                'type': 'ir.actions.act_window',
                'res_model': 'hr.attendance',
                'view_type': 'form',
                'view_mode': 'tree',
                'view_id': [res and res[1] or False],
                'context': context,
                'domain': [('id','in',new_ids)],
                }

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'tz': fields.char('Timezone', size=64, readonly=True, help='Time zone used to import dates from file. If there is no time zone UTC will be assumed'),
        'attendance_ids': fields.one2many('hr.attendance.importer.attendance', 'wizard_id', string='Attendance'),
        'file': fields.binary('File to import', required=True),
        'state': fields.selection([('import','Importing File'),('error','View Errors'),('view','View Items'),('done','Done')], string='State'),
        'result': fields.text('Result', readonly=True),
    }

    _defaults = {
        'company_id': lambda slf,cr,uid,ctx: slf.pool.get('res.company')._company_default_get(cr, uid, 'hr.attendance.importer', context=ctx),
        'tz': lambda slf,cr,uid,ctx: slf.pool.get('res.users').browse(cr, uid,uid,context=ctx).tz,
        'state': 'import'
    }