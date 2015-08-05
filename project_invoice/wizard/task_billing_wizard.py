from openerp import models, fields, api, _

class TaskBillingWizard(models.TransientModel):
    
    _name = 'task.billing.wizard'

    journal_id = fields.Many2one('account.journal', string="Journal: ")
    invoice_date = fields.Date('Invoice Date')
    
    @api.multi
    def view_init(self,fields_list):
        res = super(TaskBillingWizard, self).view_init(fields_list)
        task_obj = self.env['project.task']
        count = task_obj.search_count([('invoiced','=','tobeinvoice')])
        if not count:
            raise Warning(_('None of these task lists require invoicing.'))
        return res 
    
    def group_by_project(self, active_ids):
        task_obj = self.env['project.task']
        project_ids = []
        res={}
        for task in task_obj.browse(active_ids):
            project_ids.append(task.project_id.id)
        project_ids = list(set(project_ids))
        for project_id in project_ids:
            task = task_obj.search([('project_id', '=', project_id),('id','in',active_ids)])
            res[project_id]=task._ids
        return res
        
    @api.multi
    def create_bill_tasks(self):
        task_pool = self.env['project.task']
        active_ids = self._context.get('active_ids', [])
        data = self.group_by_project(active_ids)
        res = task_pool.action_invoice_create(data, self.journal_id.id, self.invoice_date)
        return res
        

