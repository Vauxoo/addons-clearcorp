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
		<div id = "document_data">
			<div id = "date">
				<span class="text_font">${check.date or ''|entity}</span>
			</div>
			<div id = "detail">
				<div class = "detail_line">
					<span class="text_font">${check.partner_id.name or ''|entity}</span>
				</div>
				<div class = "amount_detail">
					<span class = "amount">${formatLang(check.amount)}</span>
				</div>
			</div>
			<div class = "amount_text">
				<span class="amount_desc">${get_text(check.amount,check.currency_id,check.partner_id.lang) or ''|entity}</span>
			</div>
		</div>
		<div id = "accounting_data">
			<div id = "document_desc">
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
				<table width = "100%" id = "table_account" cellpadding = "0" cellspacing = "0">
					<thead><tr><th>&nbsp;</th><th>&nbsp;</th><th>&nbsp;</th><th>&nbsp;</th></tr></thead>
					<tbody>
					%for line in check.line_cr_ids :
					<tr class = "account_line">
						<td valign="top" class = "code_cell">
							${line.account_id.code}
						</td>
						<td valign="top" class = "account_id">
							${line.account_id.name}
						</td>
						<td valign="top" class = "amount_acc">
							${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.account_id.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}
						</td>
						<td valign="top" class = "amount_acc">
							${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.account_id.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}
						</td>
					</tr>
					%endfor
					%for line in check.line_dr_ids :
					<tr class = "account_line">
						<td valign="top" class = "code_cell">${line.account_id.code}</td>
						<td valign="top" class = "account_id">
							${line.account_id.name}
						</td>
						<td valign="top" class = "amount_acc">${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.account_id.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}</td>
						<td valign="top" class = "amount_acc">${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.account_id.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}</td>
					</tr>
					%endfor
					</tbody>
				</table>
			</div>
		</div>
	</div>
	<p style="page-break-after:always"></p>
%endfor
</body>
</html>
