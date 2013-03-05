# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Improvements + Fixes + Migration 6.0 and 6.1 Guewen Baconnier
#    Copyright 2011-2012 Camptocamp SA
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
# Fixes, improvements and V6 adaptation by Guewen Baconnier - Camptocamp 2011

from lxml import etree
from osv import fields, osv
from tools.translate import _


class res_partner_address(osv.osv):
    _inherit = 'res.partner.address'
    
    def search(self, cr, uid, args, offset=0, limit=None, order=None, 
            context=None, count=False):
        if context is None:
            context = {}
        if context.get('merge', False):
            partner_address_obj = self.pool.get('res.partner.address')
            add2 = partner_address_obj.browse(cr, uid, context['merge'], context=context).partner_id.id
            args.append(('partner_id', '=', add2))
            args.append(('id', '!=', context['merge']))
        return super(res_partner_address, self).search(cr, uid, args, offset, limit, 
                order, context=context, count=count)
res_partner_address()


class base_partner_merge_address(osv.osv_memory):
    """
    Merges two Addresses
    """
    _name = 'base.partner.merge.address'
    _description = 'Merges two addresses'

    _columns = {
        'address_id1':fields.many2one('res.partner.address', 'Address1', required=True), 
        'address_id2':fields.many2one('res.partner.address', 'Address2', required=True), 
    }

    def get_addresses(self, cr, uid, context=None):
        # wizard is launched from an address and not from the menu
        if context.get('active_model', False) != 'res.partner.address':
            return False
        ids = context.get('active_ids', False)
        if ids and not len(ids) == 2:
            raise osv.except_osv(_('Warning!'), _('You must select only two addresses'))
        return ids or False

    def _get_address1(self, cr, uid, context=None):
        ids = self.get_addresses(cr, uid, context)
        return ids and ids[0] or False

    def _get_address2(self, cr, uid, context=None):
        ids = self.get_addresses(cr, uid, context)
        if ids:
            addresses = self.pool.get('res.partner.address').\
            browse(cr, uid, ids, context=context)
            partners = []
            [partners.append(address.partner_id.id) for address in addresses]
            if len(set(partners)) > 1:
                raise osv.except_osv(_('Error'), _('Selected addresses do not belong to the same partner!'))
        return ids and ids[1] or False

    _defaults = {
            'address_id1': _get_address1,
            'address_id2': _get_address2,
    }

    def action_next(self, cr, uid, ids, context=None):

        value = {
            'name': _('Select Values'), 
            'view_type': 'form', 
            'view_mode': 'form', 
            'res_model': 'base.partner.merge.address.values', 
            'view_id': False, 
            'target': 'new', 
            'type': 'ir.actions.act_window',
            'context': str({'active_model': self._name,
                            'active_id': ids[0],
                            'active_ids': ids})
        }
        return value
base_partner_merge_address()


class base_partner_merge_address_values(osv.osv_memory):
    """
    Merges two addresses
    """
    _name = 'base.partner.merge.address.values'
    _description = 'Merges two Addresses'

    _columns = {
        'container': fields.serialized('Fields Container'),
    }

    _values = {}

    def check_addresses(self, cr, uid, add_data, context):
        """ Check validity of selected addresses.
         Inherit to add other checks
        """
        if add_data.address_id1 == add_data.address_id2:
            raise osv.except_osv(_("Error!"), _("The same address is selected in both fields."))
        return True

    def _get_previous_wizard(self, cr, uid, context=None):
        if context is None:
            context = {}
        # get address data
        merge_obj = self.pool.get('base.partner.merge.address')
        base_wiz_id = context.get('active_model') == 'base.partner.merge.address' and\
                      context.get('active_id')
        if not base_wiz_id:
            return False
        return merge_obj.browse(cr, uid, base_wiz_id, context=context)

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        res = super(base_partner_merge_address_values, self).fields_view_get(
            cr, uid, view_id, view_type, context=context, toolbar=toolbar, submenu=submenu)
        cr.execute("SELECT id, name, field_description, ttype, "
                   "required, relation, readonly "
                   "FROM ir_model_fields "
                   "WHERE model = 'res.partner.address'")
        field_datas = cr.fetchall()

        prev_wiz = self._get_previous_wizard(cr, uid, context=context)

        self.check_addresses(cr, uid, prev_wiz, context)

        form_xml, merge_fields, self._values, columns = self.pool.get('base.partner.merge')._build_form(
            cr, uid, field_datas, prev_wiz.address_id1, prev_wiz.address_id2)
        self._columns.update(columns)

        eview = etree.fromstring(res['arch'])

        placeholder = eview.xpath("//label[@string='placeholder']")[0]
        placeholder.getparent().replace(placeholder, form_xml)

        sep_diff = eview.xpath("//separator[@name='sep_diff']")[0]
        if merge_fields:
            sep_txt = "Select which data to use for the new record"
        else:
            sep_txt = "Merge Records"
        sep_diff.set('string', _(sep_txt))

        res['arch'] = etree.tostring(eview, pretty_print=True)

        res['fields'] = merge_fields
        return res

    def cast_many2one_fields(self, cr, uid, data_record, context=None):
        """ Some fields are many2one and the ORM expect them to be integer or in the form
        'relation,1' wher id is the id.
         As some fields are displayed as selection in the view, we cast them in integer.
        """
        cr.execute("SELECT name from ir_model_fields "
                   "WHERE model = 'res.partner.address' "
                   "AND ttype = 'many2one'")
        fields = cr.fetchall()
        for field in fields:
            if data_record.get(field[0], False):
                data_record[field[0]] = int(data_record[field[0]])
        return data_record

    def action_merge(self, cr, uid, ids, context=None):
        pool = self.pool
        address_obj = pool.get('res.partner.address')
        prev_wiz = self._get_previous_wizard(cr, uid, context=context)
        add1 = prev_wiz.address_id1.id
        add2 = prev_wiz.address_id2.id

        res = self.read(cr, uid, ids, context=context)[0]
        res.update(self._values)

        if hasattr(address_obj, '_sql_constraints'):
            #for uniqueness constraint (vat number for example)...
            c_names = []
            remove_field = {}
            for const in address_obj._sql_constraints:
                c_names.append('res_partner_address_' + const[0])
            if c_names:
                c_names = tuple(map(lambda x: "'"+ x +"'", c_names))
                cr.execute("""select column_name from \
                            information_schema.constraint_column_usage u \
                            join  pg_constraint p on (p.conname=u.constraint_name) \
                            where u.constraint_name in (%s) and p.contype='u' """ % c_names)
                for i in cr.fetchall():
                    remove_field[i[0]] = None

        remove_field.update({'active': False})
        address_obj.write(cr, uid, [add1, add2], remove_field, context=context)

        res = self.cast_many2one_fields(cr, uid, res, context)

        add_id = address_obj.create(cr, uid, res, context=context)

        self.custom_updates(cr, uid, add_id, [add1, add2], context)

        # For one2many fields on res.partner.address
        cr.execute("select name, model from ir_model_fields where relation='res.partner.address' and ttype not in ('many2many', 'one2many');")
        for name, model_raw in cr.fetchall():
            if hasattr(pool.get(model_raw), '_auto'):
                if not pool.get(model_raw)._auto:
                    continue
            elif hasattr(pool.get(model_raw), '_check_time'):
                continue
            else:
                if hasattr(pool.get(model_raw), '_columns'):
                    from osv import fields
                    if pool.get(model_raw)._columns.get(name, False) and isinstance(pool.get(model_raw)._columns[name], fields.many2one):
                        model = model_raw.replace('.', '_')
                        cr.execute("update "+model+" set "+name+"="+str(add_id)+" where "+str(name)+" in ("+str(add1)+", "+str(add2)+")")
        return {}

    def custom_updates(self, cr, uid, address_id, old_address_ids, context):
        """Hook for special updates on old addresses and new address
        """
        pass

base_partner_merge_address_values()


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
