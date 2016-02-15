# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request
from openerp.addons.website_sale.controllers.main import website_sale


class website_sale_simple(website_sale):

    @http.route(
        ['/shop/confirm_order'], type='http', auth="public", website=True)
    def confirm_order(self, **post):
        context = request.context
        order = request.website.sale_get_order(context=context)
        if not order:
            return request.redirect("/shop")

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        values = self.checkout_values(post)

        self.checkout_form_save(values["checkout"])

        request.session['sale_last_order_id'] = order.id

        request.website.sale_get_order(update_pricelist=True, context=context)

        return request.redirect("/shop/payment")
