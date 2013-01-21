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

import copy
import netsvc
from osv import fields, orm
import tools
from tools.translate import _

class generic_instance_merge(orm.Model):
    _name =  "generic.instance.merge"
    _description = "Generic merging Library"
    
   
    
    def merge(self, cr, uid,obj_class, id, ids, delete_merged=False, context=None):
        '''
                redirects all references from an "obj_class" instance with id in "ids" to the instance of "id"  
                
                arguments: 
                    obj_class - string, with the name of the class to be replaced (i.e. "stock.inventory")
                    id - integer, id of the instance that will remain
                    ids - list, list of ids that will be replaced by "id" argument
                    delete_merged - boolean, if instances of "ids" should be deleted after merge
        ''' 
        
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
