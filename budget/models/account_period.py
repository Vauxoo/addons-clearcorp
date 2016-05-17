# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openerp import models, api
from openerp.exceptions import Warning
from openerp.tools.translate import _


class AccountPeriodClose(models.Model):

    _inherit = "account.period.close"

    @api.one
    def data_save(self):
        period_obj = self.env['account.period']
        distribution_obj = self.env['account.move.line.distribution']
        line_obj = self.env['account.move.line']

        line_distribution = None

        for form in self.read():
            if form['sure']:
                for _id in self._context['active_ids']:
                    # Search period selected
                    period_to_close = period_obj.browse([_id])[0]
                    # Search all periods before period selected
                    period_list = period_obj.search(
                        [('fiscalyear_id', '=',
                          period_to_close.fiscalyear_id.id),
                         ('date_stop', '<=', period_to_close.date_stop)])
                    # Search all move_lines that match with period list
                    move_line_list = line_obj.search(
                        [('period_id', 'in', period_list._ids)])
                    # Search if those lines have distribution percentage 100%
                    for line in line_obj.browse(move_line_list):
                        line_distribution_id = distribution_obj.search([
                            ('account_move_line_id', '=', line.id)])
                        line_distribution_list = distribution_obj.browse(
                            line_distribution_id)
                        for line_distribution in line_distribution_list:
                            if line_distribution.distribution_percentage < 100:
                                # Create a error that show line reference
                                raise Warning(_(
                                    """All entry lines must be distributed in a
                        100 percentage.The move line with reference: '%s' is
                        not completely distributed""") % (line.ref,))

        return super(AccountPeriodClose, self).data_save()
