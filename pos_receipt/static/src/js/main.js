openerp.pos_receipt = function (instance) {
    module = instance.point_of_sale;
    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    var round_pr = instance.web.round_precision;

    module.ReceiptScreenWidget = module.ReceiptScreenWidget.extend({
        refresh: function() {
            var order = this.pos.get('selectedOrder');
            $('.pos-receipt-container', this.$el).html(QWeb.render('PosReceipt',{
                    widget:this,
                    order: order,
                    orderlines: order.get('orderLines').models,
                    paymentlines: order.get('paymentLines').models,
                }));
        },
    });

    var _initialize_ = module.PosModel.prototype.initialize;
    module.PosModel.prototype.initialize = function(session, attributes){
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

    module.Orderline = module.Orderline.extend({
        get_display_price_without_discount: function() {
            var rounding = this.pos.currency.rounding;
            return round_pr(this.get_unit_price() * this.get_quantity(), rounding);
        },
    });

    var _orderline_export_for_printing_ = module.Orderline.prototype.export_for_printing;
    module.Orderline.prototype.export_for_printing = function() {
        var res = _orderline_export_for_printing_.call(this);
        res.price_display_without_discount = this.get_display_price_without_discount();
        return res
    };

    module.Order = module.Order.extend({
        getSubtotalWithoutDiscount: function() {
            return (this.get('orderLines')).reduce((function(sum, orderLine){
                return sum + orderLine.get_display_price_without_discount();
            }), 0);
        },
    });

    var _order_export_for_printing_ = module.Order.prototype.export_for_printing;
    module.Order.prototype.export_for_printing = function() {
        var res = _order_export_for_printing_.call(this);
        var company = this.pos.company;
        var client_vat = '';
        if (this.get('client')) {
            client_vat = this.get('client').vat;
        }
        res.subtotal_without_discount = this.getSubtotalWithoutDiscount();
        res.company.fax = company.fax
        res.client_vat = client_vat
        return res
    };
}