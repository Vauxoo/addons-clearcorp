{
	"name"        : "Rent",
	"author"      : "Clear Corp S.A.",
	"version"     : "1.0",
	"depends"     : ["base","account_asset"],
	"init_xml"    : [],
	"update_xml"  : [
					"wizard/rent_make_group.xml",
					"rent_sequence.xml",
					"rent_view.xml", 
					"rent_data.xml",
					"rent_workflow.xml", 
					"rent_contract_report.xml",
					"security/rent_security.xml",
					"security/ir.model.access.csv",],
	"category"    : "Rent",
	"active"      : False,
	"instalable"  : True,
}
