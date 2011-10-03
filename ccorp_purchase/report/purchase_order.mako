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
		<div class = "document_data">
			%if not po.state =='draft' :
			<span class="title">${_("Order Ref")} ${po.name or ''|entity}</span><br/>
			%endif
			%if not po.state =='draft' :
			<span class="title">${_("Order Ref")} ${po.name or ''|entity}</span><br/>
			%endif
			%if po.state != 'draft' :
			<span class="title">${_("Partnert Order Ref")} ${po.partner_ref or ''|entity}</span><br/>   
			%endif
			%if po.date_order:
			<span class="title">${_("Date Ordered:")} ${formatLang(po.date_order, date=True)|entity}</span> <br/>
			%endif
			<span class="title">${po.user_id.name or ''|entity}</span>
			<br/>
			<span class="title">${_("Validated By.")}: ${po.validator and po.validator.name or ''|entity}</span><br/> 
		</div>
		<!-- Header partner data -->
		<table class="partner-table">
			<tbody>
				<tr>
					<td colspan="3">
						${(po.partner_id and po.partner_id.title and po.partner_id.title.name) or ''} ${po.partner_id and po.partner_id.name or ''}
					</td>
				</tr>
				<tr>
					<td><!-- Header partner data -->
						<p style="text-align:left;">
							${_("ID Num.")}: ${po.partner_id.ref or '-'|entity}<br/>
							${_("Phone")}:${po.partner_address_id and po.partner_address_id.phone or '-'|entity}<br/>
							${_("Fax")}:${po.partner_address_id and po.partner_address_id.fax or '-'|entity}<br/>
							${_("Email")}: ${po.partner_id.email or '-'|entity}<br/>
							${_("TVA")}: ${(po.partner_id and po.partner_id.vat) or '-'|entity}
							<br/><br/>
						</p>
					</td>
					<td><!-- Shipping partner address -->
						%for addr in po.dest_address_id and po.dest_address_id or []:
						<p style="text-align:left;">
						<b>${_("Shipping address")}</b><br/>
						${(addr.partner_id and addr.partner_id.title and addr.partner_id.title.name) or '' } ${(addr.partner_id and addr.partner_id.name) or ''}<br/>
						${addr.street or ''}<br/>
						${(addr.street2 or '')}<br/>
						${addr.zip or ''} ${addr.city or ''}<br/>
						${addr.state_id and addr.state_id.name or ' '}<br/>
						${addr.country_id and addr.country_id.name or ''}<br/>
						
						</p>
						%endfor
					</td>
					<td><!-- partner address -->
						<p style="text-align:left;">
						<b>${_("Partner address")}</b><br/>
						${(po.partner_id and po.partner_id.title and po.partner_id.title.name) or ''} ${(po.partner_id and po.partner_id.name) or '' }<br/>
						${(po.partner_address_id and po.partner_address_id.street ) or ''}<br/>
						${(po.partner_address_id and po.partner_address_id.street2) or ''}<br/>
						${(po.partner_address_id and po.partner_address_id.zip) or ''} ${(po.partner_address_id and po.partner_address_id.city) or ''}<br/>
						${(po.partner_address_id and po.partner_address_id.state_id and po.partner_address_id.state_id.name) or '' }<br/>
						${(po.partner_address_id and po.partner_address_id.country_id and po.partner_address_id.country_id.name) or '' }
						</p>
					</td>
				</tr>
			</tbody>
		</table>
		<table class="data-table">
			<thead><th>Qty</th><th>[Code] Description / (Taxes)</th><th>Date Req.</th><th>Unit Price</th><th>Total Price</th></thead>
		<tbody>
		%for line in po.order_line :
			<tr>
				<td>${formatLang(line.product_qty)} ${format(line.product_uom.name)}</td>
				<td>${line.name} ${', '.join(map(lambda x: x.name, line.taxes_id))|entity}</td>
				<td>${formatLang( line.date_planned, date=True)}</td>
				<td>${po.pricelist_id.currency_id.symbol_prefix or ''|entity } ${formatLang(line.price_unit,digits=get_digits(dp='Purchase Price'))} ${po.pricelist_id.currency_id.symbol_suffix or ''|entity }</td>
				<td>${po.pricelist_id.currency_id.symbol_prefix or ''|entity } ${formatLang(line.price_subtotal)} ${po.pricelist_id.currency_id.symbol_suffix or ''|entity }</td>
			</tr>
			%if line.notes :
			<tr class = "notes"><td>${line.product_id and line.product_id.code and '[' + format(line.product_id.code) + '] '}<b>${_(Note)}:</b> ${format(line.notes)}</td></tr>
			%endif
		%endfor
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-top:2px solid"><b>${_("Sub Total")}:</b></td><td style="border-top:2px solid;text-align:right">${po.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(po.amount_untaxed)} ${po.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Taxes")}:</b></td><td style="text-align:right">${po.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(po.amount_tax)} ${po.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
		<tr><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"/><td style="border-style:none"><b>${_("Total")}:</b></td><td style="text-align:right">${po.pricelist_id.currency_id.symbol_prefix or ''|entity} ${formatLang(po.amount_total)} ${po.pricelist_id.currency_id.symbol_suffix or ''|entity}</td></tr>
		</tbody>
		</table>
		<table class="notes_table" width="40%">
			%if po.notes:
				<tr><td>Order Notes:</td><td>${format(po.notes)}</td></tr>
			%endif
		</table>
	</div>
%endfor
</body>
</html>
