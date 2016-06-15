# -*- coding: utf-8 -*-
# © 2014 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.osv import osv, fields
from openerp.tools.translate import _


class CommissionRule(osv.Model):
    """Commission Rule"""

    _name = 'sale.commission.rule'

    _description = __doc__

    def _check_post_expiration_days(self, cr, uid, ids, context=None):
        for rule in self.browse(cr, uid, ids, context=context):
            if rule.post_expiration_days < 0:
                return False
        return True

    _columns = {
        'name': fields.char('Rule Name', size=128, required=True),
        'member_ids': fields.one2many('res.users', 'sale_commission_rule_id',
                                      string='Members'),
        'post_expiration_days': fields.integer(
            string='Post-Expiration Days', required=True,
            help='Quantity of days of tolerance between the '
                 'invoice due date and the payment date.'),
        'line_ids': fields.one2many('sale.commission.rule.line',
                                    'commission_rule_id', 'Rule Lines'),
        'company_id': fields.many2one('res.company', string='Company'),
    }

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get(
            'res.company')._company_default_get(cr, uid,
                                                'sale.commission.rule',
                                                context=c),
    }

    _constraints = [
        (_check_post_expiration_days, 'Value must be greater or equal than 0.',
         ['post_expiration_days'])]


class CommissionRuleLine(osv.Model):
    """Commission Rule Line"""

    _name = 'sale.commission.rule.line'

    _description = __doc__

    _order = 'sequence asc'

    def _check_sequence(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if line.sequence < 0:
                return False
        return True

    def _check_percentages(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if (not (0.0 <= line.commission_percentage <= 100.0)) or \
                    (not (0.0 <= line.max_discount <= 100.0)):
                return False
        return True

    def _check_monthly_sales(self, cr, uid, ids, context=None):
        for line in self.browse(cr, uid, ids, context=context):
            if line.monthly_sales < 0.0:
                return False
        return True

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'sequence': fields.integer('Sequence', required=True,
                                   help='Lower sequence, more priority.'),
        'commission_percentage': fields.float('Commission (%)', digits=(16, 2),
                                              required=True),
        'commission_rule_id': fields.many2one('sale.commission.rule',
                                              string='Commission Rule'),
        'partner_category_id': fields.many2one(
            'res.partner.category', string='Partner Category',
            help='True if empty or the partner belongs to this category.'),
        'pricelist_id': fields.many2one(
            'product.pricelist', string='Pricelist',
            help='True if empty or uses this Pricelist'),
        'payment_term_id': fields.many2one(
            'account.payment.term', string='Payment Term',
            help='True if empty or belongs to the Payment Term'),
        'max_discount': fields.float('Max Discount (%)', digits=(16, 2),
                                     help='True if empty or met'),
        'monthly_sales': fields.float('Monthly Sales', digits=(16, 2),
                                      help='True if empty or met.'),
    }

    _constraints = [(_check_sequence, 'Value must be greater or equal than 0.',
                     ['sequence']),
                    (_check_percentages,
                     'Value must be greater or equal than 0 and lower '
                     'or equal than 100.',
                     ['commission_percentage', 'max_discount']),
                    (_check_monthly_sales, 'Sales can not be negative',
                     ['monthly_sales'])]

    _sql_constraints = [
        ('unique_sequence_rule', 'UNIQUE(sequence,commission_rule_id)',
         'Sequence must be unique for every line in a Commission Rule.')]


class Commission(osv.Model):
    """Commission"""

    _name = 'sale.commission.commission'

    _description = __doc__

    _order = 'invoice_id asc'

    def cancel(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'cancelled'},
                          context=context)

    def pay(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'paid'}, context=context)

    def expired(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state': 'expired'}, context=context)

    def _check_amount(self, cr, uid, ids, context=None):
        for commission in self.browse(cr, uid, ids, context=context):
            if commission.amount < 0.0:
                return False
        return True

    def _check_percentage(self, cr, uid, ids, context=None):
        for commission in self.browse(cr, uid, ids, context=context):
            if commission.invoice_commission_percentage < 0.0 or \
                            commission.invoice_commission_percentage > 100.0:
                return False
        return True

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for item in self.browse(cr, uid, ids, context=context):
            res.append((item.id, '%s - %s' % (
                item.user_id.name, item.invoice_id.number)))
        return res

    def unlink(self, cr, uid, ids, context=None):
        for commission in self.browse(cr, uid, ids, context=context):
            commission.payment_id.write({'commission': False}, context=context)
        return super(Commission, self).unlink(cr, uid, ids, context=context)

    def copy(self, cr, uid, id, default=None, context=None):
        raise osv.except_osv(
            _('Failed to copy the record'),
            _('Commissions can not be copied in order to '
              'maintain integrity with the payments.'))

    def create(self, cr, uid, values, context=None):
        commission_id = super(Commission, self).create(cr, uid, values,
                                                       context=context)
        commission = self.browse(cr, uid, commission_id, context=context)
        commission.payment_id.write({'commission': True}, context=context)
        return commission_id

    def write(self, cr, uid, ids, values, context=None):
        if not isinstance(ids, list):
            ids = [ids]
        if 'payment_id' in values:
            # Get the new assigned payment
            new_payment = values['payment_id']
            # Update all payments involved and set commission to False
            move_line_obj = self.pool.get('account.move.line')
            for payment_data in self.read(cr, uid, ids, ['payment_id'],
                                          context=context):
                move_line_obj.write(cr, uid, payment_data['payment_id'][0],
                                    {'commission': False}, context=context)
            # Update the new payment and set commission to True
            move_line_obj.write(cr, uid, new_payment, {'commission': True},
                                context=context)
        return super(Commission, self).write(cr, uid, ids, values,
                                             context=context)

    _columns = {
        'invoice_id': fields.many2one('account.invoice', string='Invoice',
                                      required=True),
        'period_id': fields.related(
            'invoice_id', 'period_id', type='many2one', obj='account.period',
            string='Period', readonly=True),
        'currency_id': fields.related(
            'invoice_id', 'currency_id', type='many2one', obj='res.currency',
            string='Currency', readonly=True),
        'payment_id': fields.many2one('account.move.line', string='Payment',
                                      required=True),
        'date_invoice': fields.related(
            'invoice_id', 'date_invoice', type='date', string='Invoice Date',
            readonly=True),
        'state': fields.selection(
            [('new', 'New'), ('paid', 'Paid'), ('expired', 'Expired'),
             ('cancelled', 'Cancelled')], string='State'),
        'user_id': fields.many2one('res.users', string='Salesperson',
                                   required=True),
        'amount_base': fields.float('Base Amount', digits=(16, 2)),
        'amount': fields.float('Amount', digits=(16, 2)),
        'invoice_commission_percentage': fields.float('Commission (%)',
                                                      digits=(16, 2)),
        'company_id': fields.many2one('res.company', string='Company'),
    }

    _constraints = [
        (_check_amount, 'Value must be greater than 0.', ['amount']),
        (_check_percentage, 'Value must be greater than 0 and '
                            'lower or equal than 100',
         ['invoice_commission_percentage'])]

    _sql_constraints = [('unique_payment', 'UNIQUE(payment_id)',
                         'Only one commission can be associated '
                         'with a specific payment.')]

    _defaults = {
        'state': 'new',
        'company_id': lambda self, cr, uid, c: self.pool.get(
            'res.company')._company_default_get(cr, uid,
                                                'sale.commission.commission',
                                                context=c),
    }
