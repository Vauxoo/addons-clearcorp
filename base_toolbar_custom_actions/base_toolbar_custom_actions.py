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

import osv
import copy
from openerp.osv.orm import BaseModel

#First copy the orginal method to avoid recursion
fields_view_get_original = copy.deepcopy(osv.orm.BaseModel.fields_view_get)

#Definition of the new method
def fields_view_get2 (self, cr, user, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
    #Call to the original method to keep the upstream code running and avoid outdates of this module
    result = fields_view_get_original(self, cr, user, view_id, view_type, context, toolbar, submenu)
    #Check if there is a toolbar key in both dicts: the result and the context
    if "toolbar" in result and "toolbar" in context:
        toolbar = result["toolbar"]
        toolbar_context = context["toolbar"]
        #Check if action (Actions in toolbar) is defined in toolbar and restricted in context
        if "action" in toolbar and "action" in toolbar_context:
            #Iterate in Actions of toolbar to check if there are listed in context
            for action in toolbar["action"]:
                #Remove not listed items in domain
                if not action["res_model"] in toolbar_context["action"]:
                    toolbar["action"].remove(action)
        #Check if print (Reports in toolbar) is defined in toolbar and restricted in context
        if "print" in toolbar and "print" in toolbar_context:
            #Iterate in Reports of toolbar to check if there are listed in context
            for print_ in toolbar["print"]:
                #Remove not listed items in domain
                if not print_["report_name"] in toolbar_context["print"]:
                    toolbar["print"].remove(print_)
        #Check if relate (Links in toolbar) is defined in toolbar and restricted in context
        if "relate" in toolbar and "relate" in toolbar_context:
            #Iterate in Links of toolbar to check if there are listed in context
            for relate in toolbar["relate"]:
                #Remove not listed items in domain
                if not relate["res_model"] in toolbar_context["relate"]:
                    toolbar["relate"].remove(relate)
    return result

#Replacement of the method in the original class
osv.orm.BaseModel.fields_view_get = fields_view_get2
