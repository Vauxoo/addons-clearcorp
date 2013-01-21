import copy
import netsvc
from osv import fields, orm
import tools
from tools.translate import _

class generic_instance_merge(orm.Model):
    _name =  "generic.instance.merge"
    _description = "Generic merging Library"
    
    def merge(self, cr, uid,obj_class, id, ids, delete_merged=False, context=None):
        obj_class = obj_class.replace(".","_")
        dependencies_query = 'SELECT A.relname AS tabla, C.attname AS columna, B.relname AS tabla_foranea, D.attname AS columna_foranea ' \
            'FROM pg_catalog.pg_constraint, pg_catalog.pg_class AS A, pg_catalog.pg_class AS B, pg_catalog.pg_attribute C, pg_catalog.pg_attribute D ' \
            'WHERE contype = '+"\'"+'f'+"\' "\
            'AND conrelid = A.oid '\
            'AND confrelid = B.oid '\
            'AND conrelid = C.attrelid '\
            'AND confrelid = D.attrelid '\
            'AND C.attnum = pg_catalog.pg_constraint.conkey[1] '\
            'AND D.attnum = pg_catalog.pg_constraint.confkey[1] '\
            'AND B.relname ='+"\'"+ obj_class +"\' " \
            'AND D.attname ='+"\'id\' " \
            'ORDER BY tabla, columna, tabla_foranea, columna_foranea;'
        cr.execute(dependencies_query)
        for line in cr.fetchall():
            referencing_table = line[0]
            referencing_field = line[1] 
            for merging_id in ids:
                update_query="UPDATE "+ referencing_table + \
                " SET "+ referencing_field +" = "+ str(id) + \
                " WHERE "+ referencing_field +" = "+ str(merging_id) 
                cr.execute(update_query)
        if delete_merged:
            for deleting_id in ids: 
                if deleting_id != id:
                    delete_query = "DELETE FROM "+ obj_class + \
                        " WHERE id = "+ str(deleting_id)
                    cr.execute(delete_query)
        return True
