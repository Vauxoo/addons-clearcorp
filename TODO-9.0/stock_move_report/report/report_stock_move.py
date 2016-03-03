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
import operator
import itertools
from openerp import models
from openerp.report import report_sxw
from openerp.tools.translate import _


class StockMoveReport(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(StockMoveReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update(
            {'opening_quantity': 0.0,
             'final_cost': 0.0,
             'final_quantity': 0.0,
             'get_date_from': self.get_date_from,
             'get_date_to': self.get_date_to,
             'get_products': self.get_products,
             'get_name_product': self.get_name_product,
             'get_group_moves': self.get_group_moves,
             'get_locations': self.get_locations,
             'get_opening_quantity': self.get_opening_quantity,
             'get_opening_cost': self.get_opening_cost,
             'get_final_quantity': self.get_final_quantity,
             'get_standard_price': self.get_standard_price,
             'display_category_product': self.display_category_product,
             'get_include_costs': self.get_include_costs,
             'display_partner': self.display_partner,
             'display_source_location': self.display_source_location,
             'display_destination_location': self.display_destination_location,
             'display_picking_type': self.display_picking_type,
             'display_product': self.display_product,
             'has_stock_moves': self.has_stock_moves,
             'set_opening_quantity': self.set_opening_quantity,
             'return_opening_quantity': self.return_opening_quantity,
             'return_final_cost': self.return_final_cost,
             })

# ###########################Read Data#######################################
    def _get_info(self, data, field, model):
        info = data.get('form', {}).get(field)
        if info:
            if self.pool.get(model).browse(self.cr, self.uid, info):
                return self.pool.get(model).browse(self.cr, self.uid, info)
        return False

    def _get_form_param(self, param, data, default=False):
        return data.get('form', {}).get(param, default)
# ###########################Report Functions################################

    def get_date_from(self, data):
        return self._get_form_param('date_from', data)

    def get_date_to(self, data):
        return self._get_form_param('date_to', data)

    def get_include_costs(self, data):
        return self._get_form_param('include_costs', data)

    def get_category_ids(self, data):
        return self._get_info(data, 'category_ids', 'product.category')

    def get_product_ids(self, data):
        return self._get_info(data, 'product_ids', 'product.product')

    def get_source_location_ids(self, data):
        return self._get_info(data, 'source_location_ids', 'stock.location')

    def get_destination_location_ids(self, data):
        return self._get_info(data, 'destination_location_ids',
                              'stock.location')

    def get_picking_type_ids(self, data):
        return self._get_info(data, 'picking_type_ids', 'stock.picking.type')

    def get_partner_ids(self, data):
        return self._get_info(data, 'partner_ids', 'res.partner')

    def get_products(self, product_ids):
        return self.pool.get('product.product').browse(self.cr, self.uid,
                                                       product_ids)

    def get_search_criteria(self, data, product_id):
        partner_ids = []
        source_location_ids = []
        destination_location_ids = []
        picking_type_ids = []

        date_from = self.get_date_from(data)  # Filter type date
        date_to = self.get_date_to(data)

        partner_list = self.get_partner_ids(data)  # Filter Partners
        if partner_list:
            for partner in partner_list:
                partner_ids.append(partner.id)
        else:
            partner_ids = self.pool.get('res.partner').search(self.cr,
                                                              self.uid, [])

        source_location_list = self.get_source_location_ids(data)
        if source_location_list:
            for source_location in source_location_list:
                source_location_ids.append(source_location.id)
        else:
            source_location_ids = \
                self.pool.get('stock.location').search(self.cr, self.uid, [])

        destination_location_list = self.get_destination_location_ids(data)
        if destination_location_list:
            for destination_location in destination_location_list:
                destination_location_ids.append(destination_location.id)
        else:
            destination_location_ids = \
                self.pool.get('stock.location').search(self.cr, self.uid, [])

        picking_type_list = self.get_picking_type_ids(data)
        if picking_type_list:
            for picking_type in picking_type_list:
                picking_type_ids.append(picking_type.id)
        else:
            picking_type_ids = \
                self.pool.get('stock.picking.type').search(self.cr,
                                                           self.uid, [])

        return product_id, date_from, date_to, partner_ids,\
            source_location_ids, destination_location_ids, picking_type_ids

    def get_moves_lines(self, data, product_id, location_id):
        stock_lines_obj = self.pool.get('stock.move')

        product_id, date_from, date_to, partner_ids, source_location_ids,\
            destination_location_ids, picking_type_ids = \
            self.get_search_criteria(data, product_id)

        if location_id:  # One location
            moves_ids =\
                stock_lines_obj.search(
                    self.cr, self.uid,
                    ['&', '&', '&', '&', '&', '|', '|',
                     ('picking_id.partner_id', '=', False),
                     ('picking_id.partner_id', 'in', partner_ids),
                     ('picking_id.partner_id.parent_id', 'in', partner_ids),
                     ('picking_id.picking_type_id', 'in', picking_type_ids),
                     ('date', '>=', date_from), ('date', '<=', date_to),
                     ('product_id', '=', product_id), '|',
                     ('location_id', '=', location_id),
                     ('location_dest_id', '=', location_id)],
                    order="date asc", context=None)
        else:  # All locations
            moves_ids =\
                stock_lines_obj.search(
                    self.cr, self.uid,
                    ['&', '&', '&', '&', '&', '|', '|',
                     ('picking_id.partner_id', '=', False),
                     ('picking_id.partner_id', 'in', partner_ids),
                     ('picking_id.partner_id.parent_id', 'in', partner_ids),
                     ('picking_id.picking_type_id', 'in', picking_type_ids),
                     ('date', '>=', date_from),
                     ('date', '<=', date_to),
                     ('product_id', '=', product_id), '|',
                     ('location_id', 'in', source_location_ids),
                     ('location_dest_id', 'in', destination_location_ids)],
                    context=None)
        moves_obj = stock_lines_obj.browse(self.cr, self.uid, moves_ids,
                                           context=None)

        return moves_obj

    def search_criteria_opening_info(self, data):
        partner_ids = []
        picking_type_ids = []

        date_from = self.get_date_from(data)

        partner_list = self.get_partner_ids(data)
        if partner_list:
            for partner in partner_list:
                partner_ids.append(partner.id)
        else:
            partner_ids =\
                self.pool.get('res.partner').search(self.cr, self.uid, [])

        picking_type_list = self.get_picking_type_ids(data)
        if picking_type_list:
            for picking_type in picking_type_list:
                picking_type_ids.append(picking_type.id)
        else:
            picking_type_ids =\
                self.pool.get('stock.picking.type').search(self.cr, self.uid,
                                                           [])

        return date_from, partner_ids, picking_type_ids

# ##############Display Data###################
    def display_category_product(self, data):
        name = ''
        if not self.get_category_ids(data):
            return _('All Categories')
        else:
            categories = self.get_category_ids(data)
            for category in categories:
                name += category.name + ' , '
            return name[:-2]

    def display_product(self, data):
        name = ''
        if not self.get_product_ids(data):
            return _('All Products')
        else:
            products = self.get_product_ids(data)
            for product in products:
                name += product.name + ' , '
            return name[:-2]

    def display_partner(self, data):
        name = ''

        if not self.get_partner_ids(data):
            return _('All Companies')
        else:
            partners = self.get_partner_ids(data)
            for partner in partners:
                name += partner.name + ' , '
            return name[:-2]

    def display_source_location(self, data):
        name = ''

        if not self.get_source_location_ids(data):
            return _('All Locations')
        else:
            locations = self.get_source_location_ids(data)
            for location in locations:
                name += location.complete_name + ' , '
            return name[:-2]

    def display_destination_location(self, data):
        name = ''

        if not self.get_destination_location_ids(data):
            return _('All Locations')
        else:
            locations = self.get_destination_location_ids(data)
            for location in locations:
                name += location.complete_name + ' , '
            return name[:-2]

    def display_picking_type(self, data):
        name = ''

        if not self.get_picking_type_ids(data):
            return _('All Picking Types')
        else:
            pickings = self.get_picking_type_ids(data)
            for picking in pickings:
                name += picking.name + ' , '
            return name[:-2]

    def get_name_product(self, product_id):
        product_product_obj = self.pool.get('product.product')
        product = product_product_obj.browse(self.cr, self.uid, product_id)
        name = product.name
        if product.default_code:
            name = product.default_code + ' - ' + product.name
        return name

    def has_stock_moves(self, data, product_id):   # Exists a stock moves
        lines_obj = self.get_moves_lines(data, product_id, None)
        if lines_obj:
            return True
        return False

    def get_locations(self, data, product_id):
        line_report = {}
        stock_moves = []
        group_location = []
        source_location_ids = []
        destination_location_ids = []
        if self.get_source_location_ids(data):
            for loc in self.get_source_location_ids(data):
                source_location_ids.append(loc.id)
        else:
            for loc in self.pool.get('stock.location').search(self.cr,
                                                              self.uid, []):
                source_location_ids.append(loc)
        if self.get_destination_location_ids(data):
            for loc in self.get_destination_location_ids(data):
                destination_location_ids.append(loc.id)
        else:
            for loc in self.pool.get('stock.location').search(self.cr,
                                                              self.uid, []):
                destination_location_ids.append(loc)
        lines_obj = self.get_moves_lines(data, product_id, None)
        for line in lines_obj:
            if line.location_id.id in source_location_ids:
                line_report = {}
                line_report['location_id'] = line.location_id.id
                line_report['complete_name'] = line.location_id.complete_name
                stock_moves.append(line_report)
            if line.location_dest_id.id in destination_location_ids:
                line_report = {}
                line_report['location_id'] = line.location_dest_id.id
                line_report['complete_name'] =\
                    line.location_dest_id.complete_name
                stock_moves.append(line_report)
        locations_list = [dict(tupleized) for tupleized in
                          set(tuple(item.items()) for item in stock_moves)]
        for key, items in itertools.groupby(
                locations_list, operator.itemgetter('location_id')):
            group_location.append(list(items))
        return group_location

    def get_group_moves(self, data, product_id, location_id, opening_quantity):
        stock_moves = []
        self.localcontext['final_quantity'] = opening_quantity
        lines_obj = self.get_moves_lines(data, product_id, location_id)
        for line in lines_obj:
            if (line.location_id.id == location_id or
                    line.location_dest_id.id == location_id):

                _final_quantity = self.get_product_quantity(line, location_id,
                                                            opening_quantity)
                final_cost = self.get_opening_cost(data, product_id,
                                                   location_id,
                                                   opening_quantity)
                sign = 1
                line_report = {}
                line_report['date'] = line.date
                line_report['origin'] = line.origin or ''
                line_report['company'] = line.picking_id.partner_id.name or ''

                if line.location_id.id == location_id:
                    line_report['quantity_input'] = 0.00
                    line_report['quantity_output'] = line.product_qty or 0.00
                    self.localcontext['final_quantity'] -= line.product_qty
                    line_report['final_quantify_move'] =\
                        self.localcontext['final_quantity']
                    sign = -1
                elif line.location_dest_id.id == location_id:
                    line_report['quantity_input'] = line.product_qty or 0.00
                    line_report['quantity_output'] = 0.00
                    self.localcontext['final_quantity'] += line.product_qty
                    line_report['final_quantify_move'] =\
                        self.localcontext['final_quantity']

                line_report['standard_price'], total =\
                    self.get_standard_price(data, line)
                line_report['total'] = total
                final_cost += total * sign
                line_report['final_cost'] = final_cost
                self.localcontext['final_cost'] = final_cost
                line_report['final_cost'] = final_cost
                stock_moves.append(line_report)

        return stock_moves

    def get_opening_quantity(self, data, product_id, location_id):
        opening_quantity = 0.0
        stock_move_obj = self.pool.get('stock.move')

        date_from, partner_ids, picking_type_ids =\
            self.search_criteria_opening_info(data)

        stock_move_ids = stock_move_obj.search(
            self.cr, self.uid,
            ['&', '&', '&', '&', '|', '|',
             ('picking_id.partner_id', '=', False),
             ('picking_id.partner_id', 'in', partner_ids),
             ('picking_id.partner_id.parent_id', 'in', partner_ids),
             ('picking_id.picking_type_id', 'in', picking_type_ids),
             ('date', '<', date_from),
             ('product_id', '=', product_id), '|',
             ('location_id', '=', location_id),
             ('location_dest_id', '=', location_id)])
        stock_moves = stock_move_obj.browse(self.cr, self.uid, stock_move_ids)

        for stock_move in stock_moves:
            opening_quantity = self.get_product_quantity(stock_move,
                                                         location_id,
                                                         opening_quantity)
        return opening_quantity

    def set_opening_quantity(self, data, product_id, location_id):
        opening_quantity = self.get_opening_quantity(data, product_id,
                                                     location_id)
        self.localcontext['opening_quantity'] = opening_quantity
        return opening_quantity

    def return_opening_quantity(self):
        return self.localcontext['opening_quantity']

    def return_final_cost(self):
        return self.localcontext['final_cost']

    def get_final_quantity(self):
        return self.localcontext['final_quantity']

    def get_product_quantity(self, stock_move, location_id, quantity):
        if stock_move.location_id.id == location_id:
            quantity = quantity - stock_move.product_qty
        elif stock_move.location_dest_id.id == location_id:
            quantity = quantity + stock_move.product_qty
        return quantity

    def get_standard_price(self, data, stock_move):
        standart_price = 0.0
        total = 0.0
        quantity = 0.0
        final_cost_quant = 0.0
        if stock_move.quant_ids:
            for quant in stock_move.quant_ids:
                    quantity += abs(quant.qty)
                    final_cost_quant += (quant.cost)*abs(quant.qty)
            standart_price = (final_cost_quant/quantity)
            total = standart_price*stock_move.product_qty
        return standart_price, total

    def get_opening_cost(self, data, product_id, location_id,
                         opening_quantity):
        opening_cost = 0.0
        quantity = 0.0
        cost_quant = 0.0
        stock_move_obj = self.pool.get('stock.move')

        date_from, partner_ids, picking_type_ids =\
            self.search_criteria_opening_info(data)

        stock_move_ids = stock_move_obj.search(
            self.cr, self.uid,
            ['&', '&', '&', '&', '|', '|',
             ('picking_id.partner_id', '=', False),
             ('picking_id.partner_id', 'in', partner_ids),
             ('picking_id.partner_id.parent_id', 'in', partner_ids),
             ('picking_id.picking_type_id', 'in', picking_type_ids),
             ('date', '<', date_from),
             ('product_id', '=', product_id), '|',
             ('location_id', '=', location_id),
             ('location_dest_id', '=', location_id)])
        stock_moves = stock_move_obj.browse(self.cr, self.uid, stock_move_ids)
        if stock_moves:
            for stock_move in stock_moves:
                for quant in stock_move.quant_ids:
                    quantity += abs(quant.qty)
                    cost_quant += (quant.cost)*abs(quant.qty)
            if cost_quant != 0.0:
                opening_cost = (cost_quant/quantity)*opening_quantity
        return opening_cost


class report_stock_move_pdf(models.AbstractModel):
    _name = 'report.stock_move_report.report_stock_move_pdf'
    _inherit = 'report.abstract_report'
    _template = 'stock_move_report.report_stock_move_pdf'
    _wrapped_report_class = StockMoveReport


class report_stock_move_xls(models.AbstractModel):
    _name = 'report.stock_move_report.report_stock_move_xls'
    _inherit = 'report.abstract_report'
    _template = 'stock_move_report.report_stock_move_xls'
    _wrapped_report_class = StockMoveReport
