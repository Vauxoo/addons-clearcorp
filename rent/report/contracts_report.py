import time
from report import report_sxw

class contracts_report(report_sxw.rml_parse):
	def __init__(self,cr,uid,name,context):
		super(contracts_report,self).__init__(cr,uid,name,context)
		self.localcontext.update({
			'time' : time,
		})
report_sxw.report_sxw('report.contracts_report','rent.contract', 'addons/rent/report/contracts.rml', parser=contracts_report,header=True)
