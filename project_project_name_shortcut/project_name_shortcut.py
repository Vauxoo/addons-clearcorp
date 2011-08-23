from osv import osv, fields
from tools import debug


class project_name_shortcut(osv.osv):
	
	_inherit = 'project.project'
	
	def _shortcut_name(self, cr, uid, ids,field_name,arg, context=None):
		
		res ={}
		debug(ids)
		for m in self.browse(cr,uid,ids,context=context):
			debug(m.parent_id.name)
			
			alt_name = (m.parent_id and (m.parent_id.name + '/') or '')
			res[m.id] = alt_name + (m.partner_id and (m.partner_id.name + '/') or '') + m.name
			
		return res
		
	_columns = {
		'shortcut_name': fields.function(_shortcut_name, method=True, string='Nombre del Proyecto', type='char', size=350),
	}
project_name_shortcut()


