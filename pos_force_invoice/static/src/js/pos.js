odoo.define('pos_force_invoice.pos', function (require){
"use strict";
    var screens = require('point_of_sale.screens');
    screens.PaymentScreenWidget.include({
        validate_order: function() {
            var self = this;
            var order = this.pos.get_order();
            order.set_to_invoice(true);
            return this._super();
        }
    });
});
