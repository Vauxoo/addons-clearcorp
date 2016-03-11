# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class AccountJournal(models.Model):

    _name = 'account.journal'
    _inherit = 'account.journal'

    code = fields.Char('Code', size=64,
                       required=True,
                       help="The code will be displayed on reports.")
