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

import logging
from openerp.osv import osv
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class ProjectTask(osv.Model):

    _inherit = 'project.task'

    def action_close(self, cr, uid, ids, context=None):
        """ This action closes the task
        """
        task_id = len(ids) and ids[0] or False
        if not task_id: return False
        task = self.browse(cr, uid, task_id, context=context)
        # Check if it has a project assigned
        if task.project_id:
            # Check if the project has project manager
            if task.project_id.user_id:
                # Check if logged user is not the responsible
                if task.project_id.user_id.id != uid:
                    raise osv.except_osv(_('An error occurred'),
                        _('Only the project manager is able to close this task.'))
            else:
                # Log that the task has no project manager
                _logger.info("Task with id %d has no project manager." % task_id)
        else:
            # Log that the task has no project
            _logger.info("Task with id %d has no project." % task_id)
        return super(ProjectTask, self).action_close(cr, uid, ids, context=context)