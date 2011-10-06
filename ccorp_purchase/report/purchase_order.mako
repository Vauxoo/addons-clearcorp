<html>
<head>
	<style type="text/css">
		${css}
	</style>
</head>
<body class = "data">
	%for po in objects :
	<% setLang(po.partner_id.lang) %>
	<div id="wrapper">
		<table width = "100%" class = "document_data">
			<tr class = "title">
				<td class = "document_data">
					%if po.state =='draft' :
					<span class="title">${_("Order Ref")} ${po.name or ''|entity}</span><br/>
					%endif
					%if po.state != 'draft' :
					<span class="title">${_("Order N°")} ${po.name or ''|entity}</span>
					%endif
				</td>
				<td>
					${(po.partner_id and po.partner_id.title and po.partner_id.title.name) or ''} ${po.partner_id and po.partner_id.name or ''}
				</td>
			</tr>
			<tr>
				<td><span class="title">${_("Partnert Order Ref")}
					%if po.state != 'draft' :
					 ${po.partner_ref or ''|entity}
					%endif
					</span><br/>   
				</td>
				<td>${_("ID Num.")}: ${po.partner_id.ref or '-'|entity}</td>
			</tr>
			<tr>
				<td>${_("Date Ordered:")}
					%if po.date_order:
						${formatLang(po.date_order, date=True)|entity}
					%endif</td>
				<td>${_("Phone")}:${po.partner_address_id and po.partner_address_id.phone or '-'|entity}</td>
			</tr>
			<tr>
				<td>${_("Validated By.")}: ${po.validator and po.validator.name or ''|entity}</td>
				<td>${_("Fax")}:${po.partner_address_id and po.partner_address_id.fax or '-'|entity}</td>
			</tr>
			<tr>
				<td>${_("TVA")}: ${(po.partner_id and po.partner_id.vat) or '-'|entity}</td>
				<td>${_("Email")}: ${po.partner_id.email or '-'|entity}</td>
			</tr>
			<tr class = "zone_break"><td>&nbsp;</td><td>&nbsp;</td></tr>
			<!-- Shipping partner address -->
			<!-- Invoice partner address -->
			<tr class = "title"><td>${_("Partner address")}</td><td>${_("Shipping address")}</td></tr>
			<tr><td>${(po.partner_address_id and po.partner_address_id.street ) or ''}</td><td>${(po.dest_address_id and po.dest_address_id.street ) or ''}</td></tr>
			<tr><td>${(po.partner_address_id and po.partner_address_id.street2 ) or ''}</td><td>${(po.dest_address_id and po.dest_address_id.street2 ) or ''}</td></tr>
			<tr>
				<td>${(so.partner_address_id.zip and format(so.partner_address_id.zip) + ((so.partner_address_id.city or so.partner_address_id.state_id or so.partner_address_id.country_id) and ' ' or '') or '') + (so.partner_address_id.city and format(so.partner_address_id.city) or '')}</td>
				<td>${(so.dest_address_id.zip and format(so.dest_address_id.zip) + ((so.dest_address_id.city or so.dest_address_id.state_id or so.dest_address_id.country_id) and ' ' or '') or '') + (so.dest_address_id.city and format(so.dest_address_id.city) or '')}</td>
			</tr>
			<tr>
				<td>${(so.partner_address_id.state_id and format(so.partner_address_id.state_id.name) + (so.partner_address_id.country_id and ', ' or '') or '') + (so.partner_address_id.country_id and format(so.partner_address_id.country_id.name) or '')}</td>
				<td>${(so.dest_address_id.state_id and format(so.dest_address_id.state_id.name) + (so.dest_address_id.country_id and ', ' or '') or '') + (so.dest_address_id.country_id and format(so.dest_address_id.country_id.name) or '')}</td>
			</tr>
		</table>
		
		<table id="data-table" cellspacing="3">
			<thead><th>${_("Qty")}</th><th>${_("[Code] Description / (Taxes)")}</th><th>${_("Date Req.")}</th><th>${_("Unit Price")}</th><th>${_("Total Price")}</th></thead>
		<tbody>
		<%i = 0 %>
		%for line in po.order_line :
			%if i% 2 == 0:
				<tr class = "even">
			%else:
				<tr class = "odd">
			%endif
				<td>${formatLang(line.product_qty)} ${format(line.product_uom.name)}</td>
				<td>${line.name} ${', '.join(map(lambda x: x.name, line.taxes_id))|entity}
					%if line.notes :
						<br/><span class = "notes"><b>${_("Note")}:</b> ${format(line.notes)}</span>
					%endif
				</td>
				<td>${formatLang( line.date_planned, date=True)}</td>
				<td style="text-align:right;">${po.pricelist_id.currency_id.symbol_prefix or ''|entity } ${formatLang(line.price_unit,digits=get_digits(dp='Purchase Price'))} ${po.pricelist_id.currency_id.symbol_suffix or ''|entity }</td>
				<td style="text-align:right;">${po.pricelist_id.currency_id.symbol_prefix or ''|entity } ${formatLang(line.price_subtotal)} ${po.pricelist_id.currency_id.symbol_suffix or ''|entity }</td>
			</tr>
		%endfor
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${po.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(po.amount_untaxed)} ${po.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Taxes")}:</b></td><td style="text-align:right">${po.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(po.amount_tax)} ${po.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Total")}:</b></td><td style="text-align:right">${po.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(po.amount_total)} ${po.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
		</tbody>
		</table>
		<table id="notes_table">
			%if po.notes:
				<tr><td><b>${_("Order Notes:")}</b>${format(po.notes)}</td></tr>
			%endif
		</table>
	</div>
	<p style="page-break-after:always"></p>
%endfor
</body>
</html>
