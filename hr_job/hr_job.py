# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class hr_job(models.Model):
    _inherit = 'hr.job'

    def _count_employees(self):
        nb_employees = len(self.employee_ids or [])
        self.real_no_of_employee = nb_employees
        return nb_employees

    active = fields.Boolean('Active', default= True)
    real_no_of_employee = fields.Integer(compute="_count_employees",
                                         string="Real no of employee")
