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
		<table width = "100%" class = "document_data">
			<tr class = "title">
				<td class = "document_data">
					%if inv.type == 'out_invoice' and (inv.state == 'open' or inv.state == 'paid') :
					<span class="title">${_("Electronic Invoice")} ${inv.number or ''|entity}</span>
					%elif inv.type == 'out_invoice' and inv.state == 'proforma2' :
					<span class="title">${_("PROFORMA")} ${inv.number or ''|entity}</span>
					%elif inv.type == 'out_invoice' and inv.state == 'draft' :
					<span class="title">${_("Draft Inovice")} ${inv.number or ''|entity}</span>
					%elif inv.type == 'out_invoice' and inv.state == 'cancel':
					<span class="title">${_("Canceled Invoice")} ${inv.number or ''|entity}</span>
					%elif inv.type == 'in_invoice' :
					<span class="title">${_("Supplier Invoice")} ${inv.number or ''|entity}</span>   
					%elif inv.type == 'out_refund' :
					<span class="title">${_("Refund")} ${inv.number or ''|entity}</span> 
					%elif inv.type == 'in_refund' :
					<span class="title">${_("Supplier Refund")} ${inv.number or ''|entity}</span> 
					%endif
				</td>
				<td>
					${inv.partner_id.name}
				</td>
			</tr>
			<tr>
				<td>${inv.name or '' |entity}</td>
				<td>${_("ID Num.")}: ${inv.partner_id.ref or '-'|entity}</td>
			</tr>
			<tr>
				<td>${_("Date:")} ${formatLang(inv.date_invoice, date=True)|entity}</td>
				<td>${_("Phone")}:${inv.address_invoice_id.phone or '-'|entity}</td>
			</tr>
			<tr>
				<td>${_("Due date")}: ${formatLang(inv.date_due, date=True)|entity}</td>
				<td>${_("Fax")}: ${inv.address_invoice_id.fax or '-' | entity}</td>
			</tr>
			<tr>
				<td>${_("Payment tems")}: ${inv.payment_term.name or '-' |entity}</td>
				<td colspan = "2">${_("Email")}: ${inv.address_invoice_id.email or '-'|entity}</td><td> </td>
			</tr>
			<tr>
				<td>${_("Salesman")}: ${inv.partner_id.user_id.name or  ' '|entity}</td>
				<td>&nbsp;</td>
			</tr>
			<tr class = "zone_break"><td>&nbsp;</td><td>&nbsp;</td></tr>
			<tr class = "title"><td>${_("Address")}</td><td>&nbsp;</td></tr>
			<tr><td>${inv.address_invoice_id.street or ''}</td><td>&nbsp;</td></tr>
			<tr><td>${inv.address_invoice_id.street2 or ''}</td><td>&nbsp;</td></tr>
			<tr><td>${(inv.address_invoice_id.zip and format(inv.address_invoice_id.zip) + ((inv.address_invoice_id.city or inv.address_invoice_id.state_id or inv.address_invoice_id.country_id) and ' ' or '') or '') + (inv.address_invoice_id.city and format(inv.address_invoice_id.city) + ((inv.address_invoice_id.state_id or inv.address_invoice_id.country_id) and ', ' or '') or '') + (inv.address_invoice_id.state_id and format(inv.address_invoice_id.state_id.name) + (inv.address_invoice_id.country_id and ', ' or '') or '') + (inv.address_invoice_id.country_id and format(inv.address_invoice_id.country_id.name) or '')}</td><td>&nbsp;</td></tr>
			<tr><td>&nbsp;</td><td>&nbsp;</td></tr>
		</table>
		<table id ="data-table" cellspacing = "3">
		%if inv.amount_discounted != 0:
				<thead><th>${_("Qty")}</th><th>${_("[Code] Description / (Taxes)")}</th><th>${_("Disc.(%)")}</th><th>${_("Unit Price")}</th><th>${_("Total Price")}</th></thead>
		%else:
				<thead><th>${_("Qty")}</th><th>${_("[Code] Description / (Taxes)")}</th><th>${_("Unit Price")}</th><th>${_("Total Price")}</th></thead>
		%endif
		<tbody>
		<%i = 0 %>
		%for line in inv.invoice_line :
			%if i% 2 == 0:
				<tr class = "even">
			%else:
				<tr class = "odd">
			%endif
				<td valign = "top">${formatLang(line.quantity)} ${format(line.uos_id.name)}</td>
				<td valign = "top" id="desc_col">${line.name} 
					%if line.invoice_line_tax_id != []:
						${ ', '.join([ tax.name or '' for tax in line.invoice_line_tax_id ])|entity}
					%endif
					%if line.note :
						<br/><span class = "notes"><b>${_("Note")}:</b> ${format(line.note)}</span>
					%endif
				</td>
				%if inv.amount_discounted != 0:
					<td valign = "top" style="text-align:right;">${line.discount and formatLang(line.discount) + '%' or '-'}</td>
				%endif
				<td style="text-align:right;" valign = "top">${inv.currency_id.symbol_prefix or ''|entity } ${formatLang(line.price_unit)} ${inv.currency_id.symbol_suffix or ''|entity }</td>
				<td style="text-align:right;" valign = "top">${inv.currency_id.symbol_prefix or ''|entity } ${formatLang(line.price_subtotal_not_discounted)} ${inv.currency_id.symbol_suffix or ''|entity }</td>
			</tr>
		<%i += 1%>
		%endfor
		%if inv.amount_discounted != 0:
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${inv.currency_id.symbol_prefix or ''|entity} ${formatLang(inv.amount_untaxed_not_discounted)} ${inv.currency_id.symbol_suffix or ''|entity}</td></tr>
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Discount")}:</b></td><td style="text-align:right">${inv.currency_id.symbol_prefix or ''|entity} ${formatLang(inv.amount_discounted)} ${inv.currency_id.symbol_suffix or ''|entity}</td></tr>
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Taxes")}:</b></td><td style="text-align:right">${inv.currency_id.symbol_prefix or ''|entity} ${formatLang(inv.amount_tax)} ${inv.currency_id.symbol_suffix or ''|entity}</td></tr>
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Total")}:</b></td><td style="border-top:2px solid;text-align:right">${inv.currency_id.symbol_prefix or ''|entity} ${formatLang(inv.amount_total)} ${inv.currency_id.symbol_suffix or ''|entity}</td></tr>
		%else:
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${inv.currency_id.symbol_prefix or ''|entity} ${formatLang(inv.amount_untaxed_not_discounted)} ${inv.currency_id.symbol_suffix or ''|entity}</td></tr>
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Taxes")}:</b></td><td style="text-align:right">${inv.currency_id.symbol_prefix or ''|entity} ${formatLang(inv.amount_tax)} ${inv.currency_id.symbol_suffix or ''|entity}</td></tr>
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Total")}:</b></td><td style="border-top:2px solid;text-align:right">${inv.currency_id.symbol_prefix or ''|entity} ${formatLang(inv.amount_total)} ${inv.currency_id.symbol_suffix or ''|entity}</td></tr>
		%endif
		
		</tbody>
		</table>
		<table id = "notes_table">
			%if inv.comment:
				<tr><td><b>${_("Invoice Note")}:</b> ${format(inv.comment)}</td></tr>
			%endif
			%if inv.payment_term and inv.payment_term.note:
				<tr><td><b>${_("Payment Note")}:</b> ${format(inv.payment_term and inv.payment_term.note)}</td></tr>
			%endif
		</table>
	</div>
	<p style="page-break-after:always"></p>
	%endfor
</body>
</html>
