import time
from report import report_sxw

class contract_report(report_sxw.rml_parse):
	def __init__(self,cr,uid,name,context):
		super(contract_report,self).__init__(cr,uid,name,context)
		self.localcontext.update({
			'time' : time,
		})
report_sxw.report_sxw('report.contract_report','rent.contract', 'addons/rent/report/contracts.rml', parser=contract_report,header=False)
