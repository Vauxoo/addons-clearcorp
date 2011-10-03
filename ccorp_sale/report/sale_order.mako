<html>
<head>
	<style type="text/css">
		${css}
	</style>
</head>
<body class = "data">
	%for so in objects :
	<% setLang(so.partner_id.lang) %>
	<div id="wrapper">
		<div class = "document_data">
			%if not so.state =='draft' :
			<span class="title">${_("Quotation N°")} ${so.name or ''|entity}</span><br/>
			%endif
			%if so.state != 'draft' :
			<span class="title">${_("Order N°")} ${so.name or ''|entity}</span><br/>   
			%endif
			%if so.date_order:
			<span class="title">${_("Date:")} ${formatLang(so.date_order, date=True)|entity}</span> <br/>
			%endif
			<span class="title">${so.user_id.name or ''|entity}</span>
			<br/>
			<span class="title">${_("Ref.")}: ${so.client_order_ref != "" and so.client_order_ref or ''|entity}</span><br/> 
		</div>
		<!-- Header partner data -->
		<table class="partner-table">
			<tbody>
				<tr>
					<td colspan="3">
						${so.partner_id.name}
					</td>
				</tr>
				<tr>
					<td><!-- Header partner data -->
						<p style="text-align:left;">
							${_("ID Num.")}: ${so.partner_id.ref or '-'|entity}<br/>
							${_("Phone")}:${so.address_invoice_id.phone or '-'|entity}<br/>
							${_("Fax")}: ${so.address_invoice_id.fax or '-' | entity}<br/>
							${_("Email")}: ${so.address_invoice_id.email or '-'|entity}<br/>
							${_("Confirmation date")}: ${(so.date_confirm and formatLang(so.date_confirm,date=True)) or '-'|entity}
							<br/><br/>
						</p>
					</td>
					<td><!-- Shipping partner address -->
						<p style="text-align:left;">
						${_("Invoice address")}:<br/><br/> 
						${so.address_invoice_id.street or ''}<br/>
						${so.address_invoice_id.street2 or ''}
						${(o.partner_invoice_id.zip and format(o.partner_invoice_id.zip) + ((o.partner_invoice_id.city or o.partner_invoice_id.state_id or o.partner_invoice_id.country_id) and ' ' or '') or '') + (o.partner_invoice_id.city and format(o.partner_invoice_id.city) or '')}<br/>
						${(so.partner_invoice_id.state_id and format(so.partner_invoice_id.state_id.name) + (so.partner_invoice_id.country_id and ', ' or '') or '') + (so.partner_invoice_id.country_id and format(so.partner_invoice_id.country_id.name) or '')}
						</p>
					</td>
					<td><!-- Invoice partner address -->
						<p style="text-align:left;">
						${_("Shipping address")}:<br/><br/> 
						${so.partner_shipping_id.street or ''}<br/>
						${so.partner_shipping_id.street2 or ''}
						${(so.partner_shipping_id.zip and format(so.partner_shipping_id.zip) + ((so.partner_shipping_id.city or so.partner_shipping_id.state_id or so.partner_shipping_id.country_id) and ' ' or '') or '') + (so.partner_shipping_id.city and format(so.partner_shipping_id.city) or '')}<br/>
						${(so.partner_shipping_id.state_id and format(so.partner_shipping_id.state_id.name) + (so.partner_shipping_id.country_id and ', ' or '') or '') + (so.partner_shipping_id.country_id and format(so.partner_shipping_id.country_id.name) or '')}
						</p>
					</td>
				</tr>
			</tbody>
		</table>
		<table class="data-table">
			%if discount(o) != 0:
				<thead><th>Qty</th><th>[Code] Description / (Taxes)</th><th>Disc.</th><th>Unit Price</th><th>Total Price</th></thead>
			%else:
				<thead><th>Qty</th><th>[Code] Description / (Taxes)</th><th>Unit Price</th><th>Total Price</th></thead>
			%endif
		<tbody>
		%for line in so.order_line :
			<tr>
				<td>${formatLang(line.product_uom_qty) ${format(line.product_uom.name)}}</td>
				<td>${line.name} ${line.invoice_line_tax_id != [] and (' / (' + (', '.join([ lt.description for lt in line.tax_id ])) + ')')|entity}</td>
				%if discount(o) != 0:
					<td>${line.discount and formatLang(line.discount) + '%' or '-'}</td>
				%endif
				<td>${so.currency_id.symbol_prefix or ''|entity } ${formatLang(line.price_unit)} ${so.currency_id.symbol_suffix or ''|entity }</td>
				<td>${so.currency_id.symbol_prefix or ''|entity } ${formatLang(line.price_subtotal_not_discounted)} ${so.currency_id.symbol_suffix or ''|entity }</td>
			</tr>
			%if line.notes :
			<tr class = "notes"><td>${line.product_id and line.product_id.code and '[' + format(line.product_id.code) + '] '}<b>${_(Note)}:</b> ${format(line.notes)}</td></tr>
			%endif
		%endfor
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${so.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_untaxed_not_discounted)} ${so.currency_id.symbol_suffix or ''|entity}</td></tr>
		<!--<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Discount")}:</b></td><td style="text-align:right">${so.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_discounted)} ${so.currency_id.symbol_suffix or ''|entity}</td></tr>-->
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Taxes")}:</b></td><td style="text-align:right">${so.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_tax)} ${so.currency_id.symbol_suffix or ''|entity}</td></tr>
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Total")}:</b></td><td style="border-top:2px solid;text-align:right">${so.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_total)} ${so.currency_id.symbol_suffix or ''|entity}</td></tr>
		</tbody>
		</table>
		<table class="notes_table" width="40%">
			%if so.note:
				<tr><td>Order Notes:</td><td>${format(so.note)}</td></tr>
			%endif
			%if so.payment_term and so.payment_term.note:
				<tr><td>Payment Note:</td><td>${format(so.payment_term and so.payment_term.note)}</td></tr>
			%endif
		</table>
	</div>
%endfor
</body>
</html>
