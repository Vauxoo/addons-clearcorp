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

import pytz
from datetime import datetime
from datetime import timedelta
from openerp.osv import osv, fields
from openerp.tools.translate import _

class Contract(osv.Model):

    _inherit = 'hr.contract'

    def _attendance_normal_hours_on_day(self, cr, uid, id, date, context=None):
        if isinstance(id, list):
            id = id[0]
        attendance_obj = self.pool.get('hr.attendance')
        user = self.pool.get('res.users').browse(cr, uid, uid)
        contract = self.browse(cr, uid, id, context=context)
        datefrom = date
        if user.tz: # Parse the date at 12 o'clock to UTC
            utc = pytz.timezone('UTC')
            timezone = pytz.timezone(user.tz)
            datefrom = timezone.localize(datefrom, is_dst=False) # UTC = no DST
            datefrom = datefrom.astimezone(utc)
        dateto = datefrom + timedelta(days=1)
        datefrom = datetime.strftime(datefrom,'%Y-%m-%d %H:%M:%S')
        dateto = datetime.strftime(dateto,'%Y-%m-%d %H:%M:%S')
        # Condition to find all sign_in from date day
        cond = [('employee_id','=',contract.employee_id.id),
                ('action','=','sign_in'),
                ('name','>=',datefrom),
                ('name','<',dateto)]
        attendance_ids = attendance_obj.search(cr, uid, cond, order='name asc', context=context)
        if not attendance_ids:
            return (False, 0.0)
        sum = 0.0
        for attendance in attendance_obj.browse(cr, uid, attendance_ids, context=context):
            cond = [('employee_id','=',contract.employee_id.id),
                    ('action','=','sign_out'),
                    ('name','>=',attendance.name)]
            sign_out_ids = attendance_obj.search(cr, uid, cond, limit=1, order='name asc', context=context)
            # If there is no sign_out will skip
            if not sign_out_ids:
                continue
            sign_out = attendance_obj.browse(cr, uid, sign_out_ids[0], context=context)
            date_in = datetime.strptime(attendance.name,'%Y-%m-%d %H:%M:%S')
            date_out = datetime.strptime(sign_out.name,'%Y-%m-%d %H:%M:%S')
            value = float((date_out - date_in).seconds)/3600
            if value%1 >= 0.75:
                value = int(value) + 1.0
            elif 0.75 > value%1 >= 0.35:
                value = int(value) + 0.5
            else:
                value = int(value)
            sum += value
        return (True, sum)

    def _attendance_extra_hours_on_day(self, cr, uid, id, date, context=None):
        if isinstance(id, list):
            id = id[0]
        attendance_obj = self.pool.get('hr.attendance')
        user = self.pool.get('res.users').browse(cr, uid, uid)
        contract = self.browse(cr, uid, id, context=context)
        datefrom = date
        if user.tz: # Parse the date at 12 o'clock to UTC
            utc = pytz.timezone('UTC')
            timezone = pytz.timezone(user.tz)
            datefrom = timezone.localize(datefrom, is_dst=False) # UTC = no DST
            datefrom = datefrom.astimezone(utc)
        dateto = datefrom + timedelta(days=1)
        datefrom = datetime.strftime(datefrom,'%Y-%m-%d %H:%M:%S')
        dateto = datetime.strftime(dateto,'%Y-%m-%d %H:%M:%S')
        # Condition to find all sign_in from date day
        cond = [('employee_id','=',contract.employee_id.id),
                ('action','=','action'),
                ('action_desc.action_type','=','sign_in'),
                ('name','>=',datefrom),
                ('name','<',dateto)]
        attendance_ids = attendance_obj.search(cr, uid, cond, order='name asc', context=context)
        if not attendance_ids:
            return (False, 0.0)
        sum = 0.0
        for attendance in attendance_obj.browse(cr, uid, attendance_ids, context=context):
            cond = [('employee_id','=',contract.employee_id.id),
                    ('action','=','action'),
                    ('action_desc.action_type','=','sign_out'),
                    ('name','>=',attendance.name)]
            sign_out_ids = attendance_obj.search(cr, uid, cond, limit=1, order='name asc', context=context)
            # If there is no sign_out will skip
            if not sign_out_ids:
                continue
            sign_out = attendance_obj.browse(cr, uid, sign_out_ids[0], context=context)
            date_in = datetime.strptime(attendance.name,'%Y-%m-%d %H:%M:%S')
            date_out = datetime.strptime(sign_out.name,'%Y-%m-%d %H:%M:%S')
            value = float((date_out - date_in).seconds)/3600
            if value%1 >= 0.75:
                value = int(value) + 1.0
            elif 0.75 > value%1 >= 0.35:
                value = int(value) + 0.5
            else:
                value = int(value)
            sum += value
        return (True, sum)

    _columns = {
        'is_attendance': fields.boolean('Compute from attendance'),
    }

    _defaults = {
        'is_attendance': True
    }

class PaySlip(osv.Model):

    _inherit = 'hr.payslip'
        

    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        
        res = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            if contract.is_attendance:
                attendances = {
                    'name': _("Attendance Working Hours"),
                    'sequence': 1,
                    'code': 'HN',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'contract_id': contract.id,
                }
                day_from = datetime.strptime(date_from,"%Y-%m-%d")
                day_to = datetime.strptime(date_to,"%Y-%m-%d")
                nb_of_days = (day_to - day_from).days + 1
                for day in range(0, nb_of_days):
                    had_work, working_hours = contract._attendance_normal_hours_on_day(day_from + timedelta(days=day), context=context)
                    if had_work:
                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours
                res += [attendances]
                extra = {
                    'name': _("Attendance Extra Working Hours"),
                    'sequence': 1,
                    'code': 'HE',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'contract_id': contract.id,
                }
                for day in range(0, nb_of_days):
                    had_work, working_hours = contract._attendance_extra_hours_on_day(day_from + timedelta(days=day), context=context)
                    if had_work:
                        extra['number_of_days'] += 1.0
                        extra['number_of_hours'] += working_hours
                if extra['number_of_hours'] != 0.0:
                    res += [extra]
            else:
                res += super(PaySlip, self).get_worked_day_lines(cr, uid, [contract.id], date_from, date_to, context=context)
        return res