<html>
<head>
	<style type="text/css">
		${css}
	</style>
</head>
<body class = "data">
	%for so in objects :
	<% setLang(so.partner_id.lang) %>
	<br></br>
	<div id="wrapper">
		<table width = "100%" class = "document_data">
			<tr class = "title">
                <td class = "document_data">
                    %if so.state =='draft' :
                    <span class="title">${_("Quotation N°")} ${so.name or ''|entity}</span><br/>
                    %endif
                    %if so.state != 'draft' :
                    <span class="title">${_("Order N°")} ${so.name or ''|entity}</span><br/>   
                    %endif
                </td>
                <td>
                    ${so.partner_id.name}
                </td>
            </tr>
            <tr>
                %if so.client_order_ref:
                    <td>${_("Ref.")}: ${so.client_order_ref != "" and so.client_order_ref or ''|entity}</td>
                %endif
                 <td>${_("Contact name")}: ${so.partner_order_id.name or '-'|entity}</td>
            </tr>
            <tr>
                <td>${_("Date:")}
                    %if so.date_order:
                        ${formatLang(so.date_order, date=True)|entity}
                    %endif
                </td>
                <td>${_("Client code")}: ${so.partner_id.ref or '-'|entity}</td>
            </tr>
            <tr>
                <td>${_("Expiration date")}: ${(so.expiration_date and formatLang(so.expiration_date,date=True)) or '-'|entity}</td>
                <td>${_("Job")}: ${so.partner_order_id.function or '-'|entity}</td>
               
            </tr>
            <tr>
                <td></td>
                <td>${_("Phone")}:${so.partner_order_id.phone or '-'|entity}</td>                
            </tr>
            <tr>
                <td></td>
                <td>${_("Fax")}:${so.partner_order_id.fax or '-'|entity}</td>
            </tr>
            <tr>
                <td></td>
                <td>${_("Email")}: ${so.partner_order_id.email or '-'|entity}</td>                
                <td>&nbsp;</td><td>&nbsp;</td>
            </tr>
            <tr class = "zone_break"><td>&nbsp;</td><td>&nbsp;</td></tr>
            <tr class = "title"><td>${_("Invoice address")}</td><td>${_("Shipping address")}</td></tr>
            <tr><td>${so.partner_invoice_id.street or ''}</td><td>${so.partner_shipping_id.street or ''}</td></tr>
            <tr><td>${so.partner_invoice_id.street2 or ''}</td><td>${so.partner_shipping_id.street2 or ''}</td></tr>
            <tr>
                <td>${(so.partner_invoice_id.zip and format(so.partner_invoice_id.zip) + ((so.partner_invoice_id.city or so.partner_invoice_id.state_id or so.partner_invoice_id.country_id) and ' ' or '') or '') + (so.partner_invoice_id.city and format(so.partner_invoice_id.city) or '')}</td>
                <td>${(so.partner_shipping_id.zip and format(so.partner_shipping_id.zip) + ((so.partner_shipping_id.city or so.partner_shipping_id.state_id or so.partner_shipping_id.country_id) and ' ' or '') or '') + (so.partner_shipping_id.city and format(so.partner_shipping_id.city) or '')}</td>
            </tr>
            <tr>
                <td>${(so.partner_invoice_id.state_id and format(so.partner_invoice_id.state_id.name) + (so.partner_invoice_id.country_id and ', ' or '') or '') + (so.partner_invoice_id.country_id and format(so.partner_invoice_id.country_id.name) or '')}</td>
                <td>${(so.partner_shipping_id.state_id and format(so.partner_shipping_id.state_id.name) + (so.partner_shipping_id.country_id and ', ' or '') or '') + (so.partner_shipping_id.country_id and format(so.partner_shipping_id.country_id.name) or '')}</td>
            </tr>
		</table>
		
		<table id="data-table" cellspacing="3">
			%if company.show_sale_order_footer :	
				%if discount(so) != 0:
					<thead><th>${_("Qty")}</th><th>${_("[Code] Description / (Taxes)")}</th><th>${_("Delay")}</th><th>${_("Disc.(%)")}</th><th>${_("Unit Price")}</th><th>${_("Total Price")}</th></thead>
				%else:
					<thead><th>${_("Qty")}</th><th>${_("[Code] Description / (Taxes)")}</th><th>${_("Delay")}</th><th>${_("Unit Price")}</th><th>${_("Total Price")}</th></thead>
				%endif
			%else:
				%if discount(so) != 0:
					<thead><th>${_("Qty")}</th><th>${_("[Code] Description / (Taxes)")}</th><th>${_("Disc.(%)")}</th><th>${_("Unit Price")}</th><th>${_("Total Price")}</th></thead>
				%else:
					<thead><th>${_("Qty")}</th><th>${_("[Code] Description / (Taxes)")}</th><th>${_("Unit Price")}</th><th>${_("Total Price")}</th></thead>
				%endif
			%endif
		
		<tbody>
		<%i = 0%>
		%for line in so.order_line :
			%if i% 2 == 0:
				<tr class = "even">
			%else:
				<tr class = "odd">
			%endif
				    <td valign = "top">${formatLang(line.product_uom_qty)} ${format(line.product_uom.name)}</td>
				    <td valign = "top" id="desc_col">${line.name} ${line.tax_id != [] and (' / (' + (', '.join([ lt.description for lt in line.tax_id ])) + ')') or ''|entity}
    				%if company.show_sale_order_footer:
    					<td valign = "top" style="text-align:right;">${int(line.delay)}${_("days")}</td>
    				%endif    					
				    </td>
    				%if discount(so) != 0:
    					<td valign = "top">${line.discount and formatLang(line.discount) + '%' or '-'}</td>
    				%endif
    				<td valign = "top" style="text-align:right;">${so.pricelist_id.currency_id.symbol_prefix or ''|entity } ${formatLang(line.price_unit)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity }</td>
    				<td valign = "top" style="text-align:right;">${so.pricelist_id.currency_id.symbol_prefix or ''|entity } ${formatLang(line.price_subtotal_not_discounted)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity }</td>
			    </tr>
			    %if line.notes :
    		         <tr>
    		             <td valign = "top"></td>
    		             <td valign = "top" id="desc_col">${_("Note")}: ${format(line.notes)}</td>                        
    		         </tr>
			    %endif
		<%i +=1%>
		%endfor		
		%if discount(so) != 0:
			%if company.show_sale_order_footer :
			    <% amount_discount = (so.amount_untaxed_not_discounted - so.amount_discounted) %>
				<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_untaxed_not_discounted)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
			    <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Discount")}:</b></td><td style="text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_discounted)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
				<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Sub Total with discount")}:</b></td><td style="text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(amount_discount)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>                
				<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Taxes")}:</b></td><td style="text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_tax)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
				<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Total")}:</b></td><td style="text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_total)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
			%else:
			    <% amount_discount = (so.amount_untaxed_not_discounted - so.amount_discounted) %>
				<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_untaxed_not_discounted)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
				<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Discount")}:</b></td><td style="text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_discounted)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
                <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Sub Total with discount")}:</b></td><td style="text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(amount_discount)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
				<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Taxes")}:</b></td><td style="text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_tax)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
				<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Total")}:</b></td><td style="text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_total)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
			%endif
		%else:
			%if company.show_sale_order_footer :
				<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_untaxed_not_discounted)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
				<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Taxes")}:</b></td><td style="text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_tax)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
				<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Total")}:</b></td><td style="text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_total)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
			%else:
				<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_untaxed_not_discounted)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
				<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Taxes")}:</b></td><td style="text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_tax)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
				<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Total")}:</b></td><td style="text-align:right">${so.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_total)} ${so.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
			%endif
		%endif
		</tbody>
		</table>
		<table id="notes_table">
			%if so.note:
				<tr><td><b>${_("Order Notes")}:</b>${format(so.note)}</td></tr>
			%endif
			%if so.payment_term and so.payment_term.note:
				<tr><td><b>${_("Method of payment")}:</b>${format(so.payment_term and so.payment_term.note)}</td></tr>
			%endif
		</table>
		<br>
		<br>
		<table id="responsibles_table">
			<tr><td style="border-top:1px solid"><b>${_("Realized by")}:</b> ${so.user_id.name}</td><td style="border-style:none"/><td style="border-top:1px solid"><b>${_("Authorized by")}:_________________</b></td></tr>	
			<!--<tr><td style="border-style:none"> ${company.sale_order_footer}</td><td style="border-style:none"/></tr>-->
		</table>
		%if company.show_sale_order_footer :
			<div id="custom_footer">
				<p>${company.sale_order_footer}</p>
			<div/>
		%endif
	</div>
	<p style="page-break-after:always"></p>
%endfor
</body>
</html>
