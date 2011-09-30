<html>
<head>
	<style type="text/css">
		${css}
	</style>
</head>
<body class = "data">
	%for inv in objects :
	<% setLang(inv.partner_id.lang) %>
	<div id="wrapper">
		<div class = "document_data">
			%if inv.type == 'out_invoice' :
			<span class="title">${_("Invoice")} ${inv.number or ''|entity}</span>
			%elif inv.type == 'in_invoice' :
			<span class="title">${_("Supplier Invoice")} ${inv.number or ''|entity}</span>   
			%elif inv.type == 'out_refund' :
			<span class="title">${_("Refund")} ${inv.number or ''|entity}</span> 
			%elif inv.type == 'in_refund' :
			<span class="title">${_("Supplier Refund")} ${inv.number or ''|entity}</span> 
			%endif
			<br/>
			${_("Invoice Date:")} ${formatLang(inv.date_invoice, date=True)|entity}
		</div>
		<table class="partner-table">
			<tbody>
				<tr>
					<td colspan="3">
						${inv.partner_id.name}
					</td>
				</tr>
				<tr>
					<td>
						<p style="text-align:left;">
							${_("ID Num.")}: ${inv.partner_id.ref or '-'|entity}<br/>
							${_("Phone")}:${inv.address_invoice_id.phone or '-'|entity}<br/>
							${_("Fax")}: ${inv.address_invoice_id.fax or '-' | entity}<br/>
							${_("Email")}: ${inv.address_invoice_id.email or '-'|entity}
							<br/><br/>
						</p>
					</td>
					<td>
						<p style="text-align:left;">
						${_("Address")}: ${inv.address_invoice_id.street or ''}<br/>
						${inv.address_invoice_id.street2 or ''}<br/>
						${(inv.address_invoice_id.zip and format(inv.address_invoice_id.zip) + ((inv.address_invoice_id.city or inv.address_invoice_id.state_id or inv.address_invoice_id.country_id) and ' ' or '') or '') + (inv.address_invoice_id.city and format(inv.address_invoice_id.city) + ((inv.address_invoice_id.state_id or inv.address_invoice_id.country_id) and ', ' or '') or '') + (inv.address_invoice_id.state_id and format(inv.address_invoice_id.state_id.name) + (inv.address_invoice_id.country_id and ', ' or '') or '') + (inv.address_invoice_id.country_id and format(inv.address_invoice_id.country_id.name) or '')}
						</p>
					</td>
					<td>
						<p style="text-align:left;">
						%if inv.partner_id.user_id.name:
							${_("Salesman")}: ${inv.partner_id.user_id.name|entity}<br/>
						%endif
						${_("Payment tems")}: ${inv.payment_term.name or '-' |entity}<br/>
						${_("Due date")}: ${formatLang(inv.date_invoice, date=True)|entity}<br/>
						</p>
					</td>
				</tr>
			</tbody>
		</table>
		<table class="data-table">
		<thead><th>Qty</th><th>[Code] Description / (Taxes)</th><th>Disc.</th><th>Unit Price</th><th>Total Price</th></thead>
		<tbody>
		%for line in inv.invoice_line :
			<tr>
				<td>${formatLang(line.quantity)}</td>
				<td>${line.name} 
					%if line.invoice_line_tax_id != []:
						${ ', '.join([ tax.name or '' for tax in line.invoice_line_tax_id ])|entity}
					%endif
				</td>
				<td>
					${line.discount and formatLang(line.discount) + '%' or '-'}
				</td>
				<td>${inv.currency_id.symbol_prefix|entity } ${formatLang(line.price_unit)} ${inv.currency_id.symbol_suffix|entity }</td>
				<td>${inv.currency_id.symbol_prefix|entity } ${formatLang(line.price_subtotal_not_discounted)} ${inv.currency_id.symbol_suffix|entity }</td>
			</tr>
			%if line.note :
			<tr><td>${line.product_id and line.product_id.code and '[' + format(line.product_id.code) + '] '}<b>${_(Note)}:</b> ${format(line.note)}</td></tr>
			%endif
		%endfor
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${inv.currency_id.symbol_prefix or ''|entity} ${formatLang(inv.amount_untaxed_not_discounted)} ${inv.currency_id.symbol_suffix or ''|entity}</td></tr>
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Discount")}:</b></td><td style="text-align:right">${inv.currency_id.symbol_prefix or ''|entity} ${formatLang(inv.amount_discounted)} ${inv.currency_id.symbol_suffix or ''|entity}</td></tr>
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Taxes")}:</b></td><td style="text-align:right">${inv.currency_id.symbol_prefix or ''|entity} ${formatLang(inv.amount_tax)} ${inv.currency_id.symbol_suffix or ''|entity}</td></tr>
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Total")}:</b></td><td style="border-top:2px solid;text-align:right">${inv.currency_id.symbol_prefix or ''|entity} ${formatLang(inv.amount_total)} ${inv.currency_id.symbol_suffix or ''|entity}</td></tr>
		</tbody>
		</table>
		<table class="end-table" width="40%">
			%if inv.comment:
				<tr><td>Invoice Note:</td><td>${format(inv.comment)}</td></tr>
			%endif
			%if inv.payment_term and inv.payment_term.note:
				<tr><td>Payment Note:</td><td>${format(inv.payment_term and inv.payment_term.note)}</td></tr>
			%endif
		</table>
	</div>
%endfor
</body>
</html>
