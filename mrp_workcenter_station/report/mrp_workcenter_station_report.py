from openerp.report import report_sxw
from openerp.osv import osv

class third_party_ledger(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):
        super(third_party_ledger, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_inactive_workorders': self._get_inactive_workorders,
        })

    def _get_inactive_workorders(self, station_id):
        station_obj = self.pool.get('mrp.workcenter.station.station')
        workorder_obj = self.pool.get('mrp.production.workcenter.line')
        station = station_obj.browse(self.cr, self.uid, station_id)
        workorder_ids = []
        for workorder in station.workorder_ids:
            if workorder.state not in ('cancel','done','startworking'):
                workorder_ids.append(workorder.id)
        return workorder_obj.browse(self.cr, self.uid, workorder_ids)

class report_partnerledger(osv.AbstractModel):
    _name = 'report.mrp_workcenter_station.report_workcenter_station'
    _inherit = 'report.abstract_report'
    _template = 'mrp_workcenter_station.report_workcenter_station'
    _wrapped_report_class = third_party_ledger