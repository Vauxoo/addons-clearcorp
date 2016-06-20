# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _
from datetime import datetime


class CashBudgetProgram(models.Model):
    _name = 'cash.budget.program'
    _description = 'Program'

    code = fields.Char('Code', size=64)
    name = fields.Char('Name', size=64, required=True)
    plan_id = fields.Many2one('cash.budget.plan', 'Budget plan', required=True)
    program_lines = fields.One2many(
        'cash.budget.program.line', 'program_id', string='Lines')
    previous_program_id = fields.Many2one(
        'cash.budget.program', string='Previous program')
    state = fields.Selection(related='plan_id.state', readonly=True)

    _sql_constraints = [
        ('name', 'unique(name,plan_id)',
         'The name must be unique for this budget!')
    ]

    @api.multi
    def name_get(self,):
        res = []
        for bud_prog in self:
            name = bud_prog.name
            stop_date = datetime.strptime(
                bud_prog.plan_id.date_stop, '%Y-%m-%d')
            year = datetime.strftime(stop_date, '%Y')
            rec_name = '%s(%s)' % (name, year)
            res.append((bud_prog['id'], rec_name))
        return res

    @api.model
    def make_composite_name(self, name):
        lst = []
        composite_name = ""
        space_pos = name.find(' ')
        if space_pos != -1:
            lst.append(name[0:space_pos])
            lst.append(name[space_pos+1:len(name)-1])
        else:
            lst.append(name[0:len(name)-1])
        for word in lst:
            if len(word) >= 3:
                composite_name = composite_name + word[0:3] + '-'
            else:
                composite_name = composite_name + word + '-'
        return composite_name[0:-1]

    @api.model
    def create(self, vals):
        plan_obj = self.env['cash.budget.plan']
        plan = plan_obj.browse(vals['plan_id'])
        stop_date = datetime.strptime(plan.date_stop, '%Y-%m-%d')
        year = datetime.strftime(stop_date, '%Y')
        code = year + '-' + self.make_composite_name(vals['name'])
        vals['code'] = code
        if plan.state in ('approved', 'closed'):
            raise Warning(_(
                'You cannot create a program with a approved or closed plan'))
        res = super(CashBudgetProgram, self).create(vals)
        return res

    @api.multi
    def unlink(self):
        for program in self:
            if program.plan_id.state in ('approved', 'closed'):
                raise Warning(_("""
                    You cannot delete a program that is associated with an
                    approved or closed plan"""))
        return super(CashBudgetProgram, self).unlink()

    @api.one
    def write(self, vals):
        if self.plan_id.state in ('approved', 'closed'):
            raise Warning(_(
                'You cannot modify a program with a approved or closed plan'))
        return super(CashBudgetProgram, self).write(vals)
