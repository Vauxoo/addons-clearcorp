# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from operator import itemgetter
from openerp.tools.translate import _
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time
import logging
import openerp.netsvc
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, orm, osv


##
# ACCOUNT
##
class cash_budget_account(osv.osv):
    _name = 'cash.budget.account'
    _inherit = ['mail.thread']
    _description = 'Budget Account'
    _order = "parent_left"
    _parent_order = "code"
    _parent_store = True

    def check_cycle(self, cr, uid, ids, context=None):
        """ climbs the ``self._table.parent_id`` chains for 100 levels or
        until it can't find any more parent(s)

        Returns true if it runs out of parents (no cycle), false if
        it can recurse 100 times without ending all chains
        """
        level = 100
        while len(ids):
            cr.execute('SELECT DISTINCT parent_id ' \
                       'FROM ' + self._table + ' ' \
                                               'WHERE id IN %s ' \
                                               'AND parent_id IS NOT NULL',
                       (tuple(ids),))
            ids = map(itemgetter(0), cr.fetchall())
            if not level:
                return False
            level -= 1
        return True

    def check_max_institutional_parents(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        view_type = ('institutional',)
        for account in self.browse(cr, uid, ids, context=context):
            cr.execute('SELECT count(1) ' \
                       'FROM ' + self._table + ' ' \
                                               'WHERE parent_id IS NULL ' \
                                               'AND account_type =%s',
                       view_type)
            if cr.fetchone()[0] >= 2:
                return False
        return True

    def onchange_account_parent(self, cr, uid, ids, account_type,
                                context=None):
        search_domain = [('account_type', '=', 'undefined')]
        if account_type:
            parent_type = 'view'  # default
            search_domain = [('account_type', '=', 'view')]
            if account_type == 'consolidation' or account_type == 'institutional':
                search_domain = [('account_type', '=', 'institutional')]
        return {'domain': {'parent_id': search_domain}}

    def get_composite_code(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for account in self.browse(cr, uid, ids, context=context):
            code = ''
            acc_id = account.id
            temp_account = account
            while temp_account:
                code = temp_account.code + '.' + code
                temp_account = temp_account.parent_id
            res[acc_id] = code[:-1]
        return res

    def _get_child_ids(self, cr, uid, ids, field_name, arg, context=None):
        result = {}
        for record in self.browse(cr, uid, ids, context=context):
            if record.child_parent_ids:
                result[record.id] = [x.id for x in record.child_parent_ids]
            else:
                result[record.id] = []

            if record.child_consol_ids:
                for acc in record.child_consol_ids:
                    if acc.id not in result[record.id]:
                        result[record.id].append(acc.id)
        return result

    def _get_level(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for account in self.browse(cr, uid, ids, context=context):
            # we may not know the level of the parent at the time of computation, so we
            # can't simply do res[account.id] = account.parent_id.level + 1
            level = 0
            parent = account.parent_id
            while parent:
                level += 1
                parent = parent.parent_id
            res[account.id] = level
        return res

    def _get_children_and_consol(self, cr, uid, ids, context=None):
        # this function search for all the children and all consolidated children (recursively) of the given account ids
        ids2 = self.search(cr, uid, [('parent_id', 'child_of', ids)],
                           context=context)
        ids3 = []
        for rec in self.browse(cr, uid, ids2, context=context):
            for child in rec.child_consol_ids:
                ids3.append(child.id)
        if ids3:
            ids3 = self._get_children_and_consol(cr, uid, ids3, context)
        return ids2 + ids3

    def _get_all_children(self, cr, uid, ids, context=None):
        return self.search(cr, uid, [('parent_id', 'in', ids), '|',
                                     ('active', '=', True),
                                     ('active', '=', False)], context=context)

    def on_change_active(self, cr, uid, ids, active, context=None):
        if ids:
            return {'value': {},
                    'warning': {'title': 'Warning',
                                'message': 'This action will be applied to ALL children accounts'}}
        else:
            return {'value': {}}

    _columns = {
        'active': fields.boolean('Active'),
        'code': fields.char('Code', size=64, required=True, select=1),
        'name': fields.char('Name', size=256, ),
        'account_type': fields.selection([
            ('budget', 'Budget Entry'),  # CP
            ('view', 'Budget View'),  # VP
            ('consolidation', 'Consolidation Entry'),  # PC
            ('institutional', 'Institutional View'),  # VI
        ], 'Internal Type', required=True,
            help="The 'Internal Type' is used for features available on " \
                 "different types of accounts: view can not have journal items, consolidation are accounts that " \
                 "can have children accounts for consolidations and can only have institutional views as parent, " \
                 "institutional can have only consolidation childs"),
        'parent_id': fields.many2one('cash.budget.account', 'Parent',
                                     ondelete="cascade"),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'child_parent_ids': fields.one2many('cash.budget.account', 'parent_id',
                                            'Children'),
        'child_consol_ids': fields.many2many('cash.budget.account',
                                             'cash_budget_account_consol_rel',
                                             'parent_id', 'consol_child_id',
                                             'Consolidated Children'),
        'child_id': fields.function(_get_child_ids, type='many2many',
                                    relation="cash.budget.account",
                                    string="Child Accounts"),
        'allows_reimbursement': fields.boolean('Allows reimbursement'),
        'allows_reduction': fields.boolean('Allows reduction'),
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
        'level': fields.function(_get_level, string='Level', method=True,
                                 type='integer',
                                 store={
                                     'cash.budget.account': (
                                     _get_children_and_consol,
                                     ['level', 'parent_id'], 10),
                                 })
    }

    _defaults = {
        'account_type': 'budget',
        'active': True,
        'company_id': lambda s, cr, uid, c: s.pool.get(
            'res.company')._company_default_get(cr, uid, 'account.account',
                                                context=c),
        'allows_reimbursement': False,
        'allows_reduction': False,

    }

    _check_recursion = check_cycle
    _check_inst_parents = check_max_institutional_parents

    _constraints = [
        (_check_recursion,
         'Error!\nYou cannot create recursive account templates.',
         ['parent_id']),
        (_check_inst_parents,
         'Error!\nYou can create only 1 top level institutional view.',
         ['parent_id']),
    ]
    _sql_constraints = [
        ('check_unique_cash_budget_account', 'unique (parent_id,code,company_id)',
         'The code is defined for another account with the same parent')
    ]

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        return super(cash_budget_account, self).copy(cr, uid, id, default, context)

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []
        if not len(ids):
            return res

        for r in self.read(cr, uid, ids, ['code', 'name'], context):
            rec_name = '[%s] %s' % (r['code'], r['name'])
            res.append((r['id'], rec_name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike',
                    context=None, limit=100):
        if not args:
            args = []
        if name and operator in ('=', 'ilike', '=ilike', 'like'):
            """We need all the partners that match with the ref or name (or a part of them)"""
            ids = self.search(cr, uid, ['|', ('code', 'ilike', name),
                                        ('name', 'ilike', name)] + args,
                              limit=limit, context=context)
            if ids and len(ids) > 0:
                return self.name_get(cr, uid, ids, context)
        return super(cash_budget_account, self).name_search(cr, uid, name, args,
                                                       operator=operator,
                                                       context=context,
                                                       limit=limit)

    def _get_level(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for account in self.browse(cr, uid, ids, context=context):
            # we may not know the level of the parent at the time of computation, so we
            # can't simply do res[account.id] = account.parent_id.level + 1
            level = 0
            parent = account.parent_id
            while parent:
                level += 1
                parent = parent.parent_id
            res[account.id] = level
        return res

    def _used_by_program_line(self, cr, uid, account_id, context=None):
        obj_prog_line = self.pool.get('cash.budget.program.line')
        ocurrences = obj_prog_line.search(cr, uid,
                                          [('account_id', '=', account_id)],
                                          context=context)
        if len(ocurrences) > 0:
            return True
        else:
            return False

    def unlink(self, cr, uid, ids, context=None):
        for account in self.browse(cr, uid, ids, context=context):
            if self._used_by_program_line(cr, uid, account.id,
                                          context=context):
                raise osv.except_osv(_('Error!'), _(
                    'You cannot delete an account used by a program line'))
            else:
                return super(cash_budget_account, self).unlink(cr, uid, ids,
                                                          context=context)

    def write(self, cr, uid, ids, vals, context=None):
        for account in self.browse(cr, uid, ids, context=context):
            if 'code' in vals.keys() or 'name' in vals.keys():
                if self._used_by_program_line(cr, uid, account.id,
                                              context=context):
                    raise osv.except_osv(_('Error!'), _(
                        'You cannot overwrite the code or the name of an account used by a program line'))
            if 'active' in vals.keys():
                children = self._get_all_children(cr, uid, [account.id],
                                                  context=context)
                self.write(cr, uid, children, {'active': vals['active']},
                           context=context)
        return super(cash_budget_account, self).write(cr, uid, ids, vals,
                                                 context=context)

