<html>
<head>
	<style type="text/css">
		${css}
	</style>
</head>
<body class = "data">
	%for so in objects :
	<% setLang(so.partner_id.lang) %>
	<br/>
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
				<td>${_("Date:")}
					%if so.date_order:
						${formatLang(so.date_order, date=True)|entity}
					%endif
				</td>
				<td>${_("ID Num")}: ${so.partner_id.ref or '-'|entity}</td>
			</tr>
			<tr>
				<td>${so.user_id.name or ''|entity}</td>
				<td>${_("Phone")}:${so.partner_id.phone or '-'|entity}</td>
			</tr>
			<tr>
				%if so.client_order_ref:
					<td>${_("Ref.")}: ${so.client_order_ref != "" and so.client_order_ref or ''|entity}</td>
				%endif
				<td>${_("Email")}: ${so.partner_id.email or '-'|entity}</td>
			</tr>
			<tr>
				<td>${_("Confirmation date")}: ${(so.date_confirm and formatLang(so.date_confirm,date=True)) or '-'|entity}</td>
				<td>${_("Expiration date")}: ${(so.expiration_date and formatLang(so.expiration_date,date=True)) or '-'|entity}</td>
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
			%if discount(so) != 0:
				<thead><th>${_("Qty")}</th><th>${_("[Code] Description / (Taxes)")}</th><th>${_("Disc.(%)")}</th><th>${_("Unit Price")}</th><th>${_("Total Price")}</th></thead>
			%else:
				<thead><th>${_("Qty")}</th><th>${_("[Code] Description / (Taxes)")}</th><th>${_("Unit Price")}</th><th>${_("Total Price")}</th></thead>
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
        				<td valign = "top" id="desc_col">${line.name} ${line.tax_id != [] and (' / (' + (', '.join([ lt.name for lt in line.tax_id ])) + ')') or ''|entity}
        				%if discount(so) != 0:
        					<td valign = "top">${line.discount and formatLang(line.discount) + '%' or '-'}</td>
        				%endif
        				%if so.currency_id.position == 'before':
        	       			<td valign = "top" style="text-align:right;">${so.currency_id.symbol or ''|entity}&nbsp;${formatLang(line.price_unit)}</td>
        			     	<td valign = "top" style="text-align:right;">${so.currency_id.symbol or ''|entity}&nbsp;${formatLang(line.price_subtotal_not_discounted)}</td>
        			    %else:
                            <td valign = "top" style="text-align:right;">${formatLang(line.price_unit)}&nbsp;${so.currency_id.symbol or ''|entity}</td>
                            <td valign = "top" style="text-align:right;">${formatLang(line.price_subtotal_not_discounted)}&nbsp;${so.currency_id.symbol or ''|entity}</td>
        			    %endif
        			</tr>
        		<%i +=1%>
        		%endfor		
        		%if discount(so) != 0: 
                  %if so.currency_id.position == 'before':  
                      <% amount_discount = (so.amount_untaxed_not_discounted - so.amount_discounted) %>
                      <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${so.currency_id.symbol or ''}&nbsp;${formatLang(so.amount_untaxed_not_discounted)}</td></tr>
                      <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><td style="border-style:none"/><b>${_("Discount")}:</b></td><td style="text-align:right">${so.currency_id.symbol or ''}&nbsp;${formatLang(so.amount_discounted)}</td></tr>
                      <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><td style="border-style:none"/><b>${_("Taxes")}:</b></td><td style="text-align:right">${so.currency_id.symbol or ''}&nbsp;${formatLang(so.amount_tax)}</td></tr>
                      <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><td style="border-style:none"/><b>${_("Total")}:</b></td><td style="text-align:right">${so.currency_id.symbol or ''}&nbsp;${formatLang(so.amount_total)}</td></tr>
                  %else:
                      <% amount_discount = (so.amount_untaxed_not_discounted - so.amount_discounted) %>
                      <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${formatLang(so.amount_untaxed_not_discounted)}&nbsp;${so.currency_id.symbol or ''}</td></tr>
                      <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><b>${_("Discount")}:</b></td><td style="text-align:right">${so.currency_id.symbol or ''}&nbsp;${formatLang(so.amount_discounted)}</td></tr>
                      <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><td style="border-style:none"/><b>${_("Taxes")}:</b></td><td style="text-align:right">${formatLang(so.amount_tax)}&nbsp;${so.currency_id.symbol or ''}</td></tr>
                      <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><td style="border-style:none"/><b>${_("Total")}:</b></td><td style="text-align:right">${formatLang(so.amount_total)}&nbsp;${so.currency_id.symbol or ''}</td></tr>
                  %endif
                %else:
                     %if so.currency_id.position == 'before':
                          <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${so.currency_id.symbol or ''}&nbsp;${formatLang(so.amount_untaxed_not_discounted)}</td></tr>
                          <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Taxes")}:</b></td><td style="text-align:right">${so.currency_id.symbol or ''}&nbsp;${formatLang(so.amount_tax)}</td></tr>
                          <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Total")}:</b></td><td style="text-align:right">${so.currency_id.symbol or ''}&nbsp;${formatLang(so.amount_total)}</td></tr>
                     %else:
                          <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${formatLang(so.amount_untaxed_not_discounted)}&nbsp;${so.currency_id.symbol or ''}</td></tr>
                          <tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Taxes")}:</b></td><td style="text-align:right">${formatLang(so.amount_tax)}&nbsp;${so.currency_id.symbol or ''}</td></tr>
                          <tr><td style="border-style:none"/><td style="border-style:none"><td style="border-style:none"/><b>${_("Total")}:</b></td><td style="text-align:right">${formatLang(so.amount_total)}&nbsp;${so.currency_id.symbol or ''}</td></tr>
                     %endif
        		%endif
    		</tbody>
		</table>
		<table id="notes_table">
			%if so.note:
				<tr><td><b>${_("Order Notes")}:</b>${format(so.note)}</td></tr>
			%endif
			%if so.payment_term and so.payment_term.note:
				<tr><td><b>${_("Payment Note")}:</b>${format(so.payment_term and so.payment_term.note)}</td></tr>
			%endif
		</table>
		<br>
		<br>
		<table id="responsibles_table">
			<tr><td style="border-top:1px solid"><b>${_("Realized by")}:</b> ${so.user_id.name}</td><td style="border-style:none"/><td style="border-top:1px solid"><b>${_("Authorized by")}:_________________</b></td></tr>	
		</table>		
	</div>	
%endfor
    <p style="page-break-after:always"></p>
</body>
</html>
