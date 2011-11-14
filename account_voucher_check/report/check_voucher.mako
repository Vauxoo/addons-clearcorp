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
		<table width = "100%" id = "document_data">
			<tr>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>
					<span class="text_font" id = "date">${check.date or ''|entity}</span>
				</td>
			</tr>
			<tr class = "detail">
				<td colspan = "3">
					<span class="text_font">${check.partner_id.name or ''|entity}</span>
				</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>
					<span class = "text_font">${formatLang(check.amount)}</span>
				</td>
			</tr>
			<tr class = "detail">
				<td class = "amount_text" colspan = "4">
					<span class="text_font">${check.amount_text or ''|entity}</span>
				</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
			</tr>
		</table>
		<table width = "100%" id = "document_desc">
			<thead>
				<tr style = "text-align : left;"><th>SE EMITE ESTE CHEQUE POR EL SIGUIENTE CONCEPTO</th></tr>
			</thead>
			<tr class = "part_account">
				%if check.narration:
				<td>${check.narration or ''|entity}</td>
				%else:
				<td>&nbsp;</td>
				%endif
			</tr>
		</table>
		<table width = "100%" id = "table_account">
			<thead><tr><th>CODE</th><th>ACCOUNTS AFFECTED</th><th>CREDIT</th><th>DEBIT</th><tr></thead>
			<tbody>
			%for line in check.line_cr_ids :
			<tr class = "account_line">
				<td valign="top">${line.account_id.code}</td>
				<td valign="top">
					${line.account_id.name}
				</td>
				<td valign="top">${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.account_id.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}</td>
				<td valign="top">${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.account_id.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}</td>
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
				<td><span class = "text_font">${check.partner_id.name or ''|entity}</span></td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
			</tr>
		</table>		
	</div>
	<p style="page-break-after:always"></p>
%endfor
</body>
</html>
