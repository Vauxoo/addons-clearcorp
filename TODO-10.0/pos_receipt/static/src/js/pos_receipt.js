/* © 2016 ClearCorp
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
 */
odoo.define('pos_receipt.main', function (require) {
"use strict";

var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;
var utils = require('web.utils');
var round_pr = utils.round_precision;
var screens = require('point_of_sale.screens');
var pos_models = require('point_of_sale.models');

var ReceiptScreenWidget = screens.ReceiptScreenWidget.include({
    render_receipt: function() {
        var order = this.pos.get_order();
        this.$('.pos-receipt-container').html(QWeb.render('PosReceipt', {
            widget:this,
            order: order,
            receipt: order.export_for_printing(),
            orderlines: order.get_orderlines(),
            paymentlines: order.get_paymentlines(),
        }));
    }
});

var _initialize_ = pos_models.PosModel.prototype.initialize;
pos_models.PosModel.prototype.initialize = function(session, attributes) {
    self = this;
    // Add the load of the field company.fax
    for (var i = 0 ; i < this.models.length; i++) {
        if (this.models[i].model == 'res.company'){
            if (this.models[i].fields.indexOf('fax') == -1) {
                this.models[i].fields.push('fax');
            }
        }
    }

    return _initialize_.call(this, session, attributes);
};

var _super_orderline = pos_models.Orderline.prototype;
pos_models.Orderline = pos_models.Orderline.extend({
    get_display_price_without_discount: function() {
        var rounding = this.pos.currency.rounding;
        return round_pr(this.get_unit_price() * this.get_quantity(), rounding);
    },

    export_for_printing: function() {
        var res = _super_orderline.export_for_printing.call(this);
        res.price_display_without_discount = this.get_display_price_without_discount();
        return res;
    }
});

var _super_order = pos_models.Order.prototype;
pos_models.Order = pos_models.Order.extend({
    getSubtotalWithoutDiscount: function() {
        var rounding = this.pos.currency.rounding;
        return round_pr(this.orderlines.reduce((function(sum, orderLine) {
            return sum + orderLine.get_display_price_without_discount();
        }), 0), rounding);
    },

    export_for_printing: function() {
        var res = _super_order.export_for_printing.call(this);
        var company = this.pos.company;
        var client_vat = '';
        if (this.get('client')) {
            client_vat = this.get('client').vat;
        }
        res.subtotal_without_discount = this.getSubtotalWithoutDiscount();
        res.company.fax = company.fax
        res.client_vat = client_vat
        return res
    }
});

});