from openerp import models, fields, api, _
from openerp.exceptions import Warning


class issue(models.Model):
    
    _inherit = 'project.issue'
    
    task_ids = fields.Many2many('project.task')
    work_type_id = fields.Many2one('ccorp.project.oerp.work.type','Type of work',required=True)