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
				<td>${_("ID Num.")}: ${so.partner_id.ref or '-'|entity}</td>
			</tr>
			<tr>
				<td>${so.user_id.name or ''|entity}</td>
				<td>${_("Phone")}:${so.partner_id.phone or '-'|entity}</td>
			</tr>
			<tr>
				<td>${_("Ref.")}: ${so.client_order_ref != "" and so.client_order_ref or ''|entity}</td>
				<td>${_("Email")}: ${so.partner_id.email or '-'|entity}</td>
			</tr>
			<tr>
				<td>${_("Confirmation date")}: ${(so.date_confirm and formatLang(so.date_confirm,date=True)) or '-'|entity}</td>
				<td>&nbsp;</td><td>&nbsp;</td>
			</tr>
			<tr class = "zone_break"><td>&nbsp;</td><td>&nbsp;</td></tr>
			<!-- Shipping partner address -->
			<!-- Invoice partner address -->
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
		<%i = 0 %>
		%for line in so.order_line :
			%if i% 2 == 0:
				<tr class = "even">
			%else:
				<tr class = "odd">
			%endif
				<td valign = "top">${formatLang(line.product_uom_qty)} ${format(line.product_uom.name)}</td>
				<td valign = "top">${line.name} ${line.tax_id != [] and (' / (' + (', '.join([ lt.description for lt in line.tax_id ])) + ')') or ''|entity}
					%if line.notes :
						<span class = "notes"><b>${_("Note")}:</b> ${format(line.notes)}</span>
					%endif
				</td>
				%if discount(so) != 0:
					<td valign = "top">${line.discount and formatLang(line.discount) + '%' or '-'}</td>
				%endif
				<td valign = "top" style="text-align:right;">${so.company_id.currency_id.symbol_prefix or ''|entity } ${formatLang(line.price_unit)} ${so.company_id.currency_id.symbol_suffix or ''|entity }</td>
				<td valign = "top" style="text-align:right;">${so.company_id.currency_id.symbol_prefix or ''|entity } ${formatLang(line.price_subtotal)} ${so.company_id.currency_id.symbol_suffix or ''|entity }</td>
			</tr>
		<%i +=1%>
		%endfor
		%if discount(so) != 0:
			<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${so.company_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_untaxed)} ${so.company_id.currency_id.symbol_suffix or ''|entity}</td></tr>
			<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Taxes")}:</b></td><td style="text-align:right">${so.company_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_tax)} ${so.company_id.currency_id.symbol_suffix or ''|entity}</td></tr>
			<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Total")}:</b></td><td style="text-align:right">${so.company_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_total)} ${so.company_id.currency_id.symbol_suffix or ''|entity}</td></tr>
		%else:
			<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${so.company_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_untaxed)} ${so.company_id.currency_id.symbol_suffix or ''|entity}</td></tr>
			<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Taxes")}:</b></td><td style="text-align:right">${so.company_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_tax)} ${so.company_id.currency_id.symbol_suffix or ''|entity}</td></tr>
			<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Total")}:</b></td><td style="text-align:right">${so.company_id.currency_id.symbol_prefix or ''|entity} ${formatLang(so.amount_total)} ${so.company_id.currency_id.symbol_suffix or ''|entity}</td></tr>
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
	</div>
	<p style="page-break-after:always"></p>
%endfor
</body>
</html>
