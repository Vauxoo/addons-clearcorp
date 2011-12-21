<html>
<head>
	<style style="text/css">
		${css}
	</style>
</head>
<body class = "data">
	%for check in objects :
	<% setLang(check.partner_id.lang) %>
	<div id="wrapper">
		<div width = "100%" id = "document_data">
			<div id = "date">
				<span class="text_font" id = "date">${check.date or ''|entity}</span>
			</div>
			</tr>
			<div id = "detail">
				<div class = "detail_line">
					<span class="text_font">${check.partner_id.name or ''|entity}</span>
				</div>
				<div class = "detail_line">
					<span class = "text_font">${formatLang(check.amount)}</span>
				</div>
			</div>
			<div class = "amount_detail">
				<span class="amount">${check.amount_text or ''|entity}</span>
			</div>
		</div>
		<div id = "accounting_data">
			<div width = "100%" id = "document_desc">
				<p>&nbsp;</p>
				<div class = "detail_desc">
					%if check.narration:
					<span class = "text_font">${check.narration or ''|entity}</span>
					%else:
					<span>&nbsp;</span>
					%endif
				</div>
			</div>
			<div id = "accounts">
				<table width = "100%" id = "table_account">
					<thead><tr><th>CODE</th><th>ACCOUNTS AFFECTED</th><th>CREDIT</th><th>DEBIT</th><tr></thead>
					<tbody>
					%for line in check.line_cr_ids :
					<tr class = "account_line">
						<td valign="top">
							${line.account_id.code}
						</td>
						<td valign="top">
							${line.account_id.name}
						</td>
						<td valign="top">
							${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.account_id.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}
						</td>
						<td valign="top">
							${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.account_id.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}
						</td>
					</tr>
					%endfor
					%for line in check.line_dr_ids :
					<tr class = "account_line">
						<td valign="top">${line.account_id.code}</td>
						<td valign="top">
							${line.account_id.name}
						</td>
						<td valign="top">${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.account_id.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}</td>
						<td valign="top">${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.account_id.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}</td>
					</tr>
					%endfor
					</tbody>
				</table>
				<table width = "100%" id = "footer_data">
					<tr id = "check_footer">
						<td>No.5199</td>
						<td>${user.name}</td>
						<td>${user.name}</td>
						<td><span>${check.partner_id.name or ''|entity}</span></td>
						<td>&nbsp;</td>
						<td>&nbsp;</td>
					</tr>
				</table>
			</div>
		</div>
	</div>
	<p style="page-break-after:always"></p>
%endfor
</body>
</html>
