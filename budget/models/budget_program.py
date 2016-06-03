# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api
from openerp.exceptions import Warning
from openerp.tools.translate import _
from datetime import datetime
import openerp.addons.decimal_precision as dp


class BudgetProgram(models.Model):
    _name = 'budget.program'
    _description = 'Program'

    code = fields.Char('Code', size=64)
    name = fields.Char('Name', size=64, required=True)
    plan_id = fields.Many2one('budget.plan', 'Budget plan', required=True)
    program_lines = fields.One2many(
        'budget.program.line', 'program_id', string='Lines')
    previous_program_id = fields.Many2one(
        'budget.program', string='Previous program')
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
        plan_obj = self.env['budget.plan']
        plan = plan_obj.browse(vals['plan_id'])
        stop_date = datetime.strptime(plan.date_stop, '%Y-%m-%d')
        year = datetime.strftime(stop_date, '%Y')
        code = year + '-' + self.make_composite_name(vals['name'])
        vals['code'] = code
        if plan.state in ('approved', 'closed'):
            raise Warning(_(
                'You cannot create a program with a approved or closed plan'))
        res = super(BudgetProgram, self).create(vals)
        return res

    @api.multi
    def unlink(self):
        for program in self:
            if program.plan_id.state in ('approved', 'closed'):
                raise Warning(_("""
                    You cannot delete a program that is associated with an
                    approved or closed plan"""))
        return super(BudgetProgram, self).unlink()

    @api.one
    def write(self, vals):
        if self.plan_id.state in ('approved', 'closed'):
            raise Warning(_(
                'You cannot modify a program with a approved or closed plan'))
        return super(BudgetProgram, self).write(vals)


class BudgetProgramLine(models.Model):
    _name = 'budget.program.line'
    _description = 'Program line'
    _order = "parent_left"
    _parent_order = "name"
    _parent_store = True

    name = fields.Char('Name', size=64, required=True)
    parent_id = fields.Many2one(
        'budget.program.line', string='Parent line', ondelete='cascade')
    account_id = fields.Many2one(
        'budget.account', string='Budget account', required=True)
    program_id = fields.Many2one(
        'budget.program', string='Program', required=True, ondelete='cascade')
    assigned_amount = fields.Float(
        string='Assigned amount', digits=dp.get_precision('Account'),
        fdefault=0.0, required=True)
    type = fields.Selection(
        related='account_id.account_type', string='Line Type', store=True,
        readonly=True)
    state = fields.Selection(
        related='program_id.state', string='State', readonly=True)
    total_assigned = fields.Float(compute='__compute', string='Assigned')
    extended_amount = fields.Float(compute='__compute', string='Extensions')
    modified_amount = fields.Float(compute='__compute', string='Modifications')
    reserved_amount = fields.Float(compute='__compute', string='Reservations')
    compromised_amount = fields.Float(
        compute='__compute', string='Compromises')
    executed_amount = fields.Float(compute='__compute', string='Executed')
    available_budget = fields.Float(
        compute='__compute', string='Available Budget')
    available_cash = fields.Float(compute='__compute', string='Available Cash')
    execution_percentage = fields.Float(
        compute='__compute', string='Execution Percentage')
    sponsor_id = fields.Many2one('res.partner', 'Sponsor')
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.user.company_id.id, required=True)
    parent_left = fields.Integer('Parent Left', select=True)
    arent_right = fields.Integer('Parent Right', select=True)
    child_parent_ids = fields.One2many(
        'budget.program.line', 'parent_id', string='Children')
    child_consol_ids = fields.Many2many(
        'budget.program.line', 'budget_program_line_consol_rel', 'parent_id',
        'consol_child_id', string='Consolidated Children')
    child_id = fields.Many2many(
        compute='_get_child_ids', string="Child Accounts")
    previous_year_line_id = fields.Many2one(
        'budget.program.line', 'Previous year line')
    active_for_view = fields.Boolean('Active', default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name, program_id,company_id)',
         'The name of the line must be unique per company!')
    ]

    @api.one
    def _get_children_and_consol(self, childs_ids):
        # this function search for all the children and all consolidated
        # children (recursively) of the given line ids

        child_ids = self.search([('parent_id', 'child_of', childs_ids)])\
            if self else []
        child_child_ids = []
        for child in child_ids:
            for child_child in child.child_consol_ids:
                child_child_ids.append(child_child.id)
        if child_child_ids:
            child_child_ids = self._get_children_and_consol(child_child_ids)
        return child_ids + child_child_ids

    @api.one
    def __compute(self, field_names):
        field_names = list(set(
            ['total_assigned', 'executed_amount', 'reserved_amount',
             'modified_amount', 'extended_amount', 'compromised_amount'] +
            field_names))
        children_and_consolidated = self._get_children_and_consol(self.id)
        prg_lines = {}
        _es = {}
        _null_result = dict((fn, 0.0) for fn in field_names)
        if children_and_consolidated:
            mapping = {
                'total_assigned':
                    'COALESCE(MAX(BPL.assigned_amount),0.0) AS total_assigned',
                'executed':
                    'COALESCE(SUM(BML.executed),0.0) AS executed_amount',
                'reserved':
                    'COALESCE(SUM(BML.reserved),0.0) AS reserved_amount',
                'changed': 'COALESCE(SUM(BML.changed),0.0) AS modified_amount',
                'extended':
                    'COALESCE(SUM(BML.extended),0.0) AS extended_amount',
                'compromised':
                    'COALESCE(SUM(BML.compromised),0.0) AS compromised_amount',
            }
            request = (
                'SELECT BPL.id, ' +
                ', '.join(mapping.values()) +
                'FROM budget_program_line BPL' +
                'LEFT OUTER JOIN budget_move_line' +
                'BML ON BPL.id = BML.program_line_id' +
                'WHERE BPL.id IN %s' +
                'GROUP BY BPL.id')
            params = (tuple(children_and_consolidated),)
            self.env.cr.execute(request, params)
            for row in self.env.cr.dictfetchall():
                prg_lines[row['id']] = row

            children_and_consolidated.reverse()
            brs = list(self.browse(children_and_consolidated))
            sums = {}
            while brs:
                current = brs.pop(0)
                for fn in field_names:
                    sums.setdefault(current.id, {})[fn] = prg_lines.get(
                        current.id, {}).get(fn, 0.0)
                    for child in current.child_id:
                        if child.company_id.currency_id.id ==\
                                current.company_id.currency_id.id:
                            sums[current.id][fn] += sums[child.id][fn]
                # There are 2 types of available:
                #  1-) available budget = assigned - opening + modifications +
                #      extensions - compromised - reserved - executed.
                #  2-) available cash = assigned - opening + modifications +
                #      extensions - executed
                if 'available_cash' in field_names or\
                        'available_budget' in field_names or\
                        'execution_percentage' in field_names:
                    available_budget = sums[current.id].get(
                        'total_assigned', 0.0) + sums[current.id].get(
                        'modified_amount', 0.0) + sums[current.id].get(
                        'extended_amount', 0.0) - sums[current.id].get(
                        'compromised_amount', 0.0) - sums[current.id].get(
                        'reserved_amount', 0.0) - sums[current.id].get(
                        'executed_amount', 0.0)
                    available_cash = sums[current.id].get(
                        'total_assigned', 0.0) + sums[current.id].get(
                        'modified_amount', 0.0) + sums[current.id].get(
                        'extended_amount', 0.0) - sums[current.id].get(
                        'executed_amount', 0.0)
                    grand_total = (sums[current.id].get(
                        'total_assigned', 0.0) + sums[current.id].get(
                        'modified_amount', 0.0) + sums[current.id].get(
                        'extended_amount', 0.0))
                    exc_perc = grand_total != 0.0 and ((sums[current.id].get(
                        'executed_amount', 0.0)*100) / grand_total) or 0.0
                    sums[current.id].update({
                        'available_cash': available_cash,
                        'available_budget': available_budget,
                        'execution_percentage': exc_perc})
                    self.total_assigned = sums[current.id].get(
                        'total_assigned', 0.0)
                    self.extended_amount = sums[current.id].get(
                        'extended_amount', 0.0)
                    self.modified_amount = sums[current.id].get(
                        'modified_amount', 0.0)
                    self.reserved_amount = sums[current.id].get(
                        'reserved_amount', 0.0)
                    self.compromised_amount = sums[current.id].get(
                        'compromised_amount', 0.0)
                    self.executed_amount = sums[current.id].get(
                        'executed_amount', 0.0)
                    self.available_budget = available_budget
                    self.available_cash = available_cash
                    self.execution_percentage = exc_perc

    @api.one
    @api.constrains('account_id', 'program_id')
    def _check_unused_account(self):
        # checks that the selected budget account is not associated to another
        # program line
        for line in self.read(['account_id', 'program_id']):
            self.env.cr.execute(
                'SELECT count(1) ' +
                'FROM '+self._table+' ' +
                'WHERE account_id = %s ' +
                'AND id != %s' +
                'AND program_id = %s', (line['account_id'][0], line['id'],
                                        line['program_id'][0]))

            if self.env.cr.fetchone()[0] > 0:
                raise Warning(_(
                    'There is already a program line using this budget account'
                    ))

    @api.one
    def _get_child_ids(self):
        result = {}
        if self.child_parent_ids:
            result[self.id] = [x.id for x in self.child_parent_ids]
        else:
            result[self.id] = []

        if self.child_consol_ids:
            for acc in self.child_consol_ids:
                if acc.id not in result[self.id]:
                    result[self.id].append(acc.id)
        self.child_id = result[self.id]

    @api.multi
    def get_next_year_line(self):
        res = {}
        for line in self:
            result = self.search([('previous_year_line_id', '=', line.id)])
            if result:
                res[line.id] = result[0]
            else:
                res[line.id] = None
        return res

    @api.one
    def set_previous_year_line(self):
        modified_ids = []
        previous_program_lines = self.search([
            ('program_id', '=', self.program_id.previous_program_id.id),
            ('account_id', '=', self.account_id.id)])
        if previous_program_lines:
            self.write({'previous_year_line_id': previous_program_lines[0].id})
            modified_ids.append(self.id)
        return modified_ids

    @api.multi
    def unlink(self):
        for line in self:
            if line.program_id.plan_id.state in ('approved', 'closed'):
                raise Warning(_(
                    'You cannot delete a line from an approved or closed plan'
                ))
        return super(BudgetProgramLine, self).unlink()

    @api.one
    def write(self, vals):
        if self.program_id.plan_id.state in ('approved', 'closed'):
            if len(vals) == 1 and 'active_for_view' in vals.keys():
                pass
            else:
                raise Warning(_(
                    'You cannot modify a line from an approved or closed plan'
                ))
        return super(BudgetProgramLine, self).write(vals)

    @api.model
    def create(self, vals):
        program_obj = self.env['budget.program']
        program = program_obj.browse([vals['program_id']])
        if program.plan_id.state in ('approved', 'closed'):
            raise Warning(_(
                'You cannot create a line from an approved or closed plan'))

        return super(BudgetProgramLine, self).create(vals)
