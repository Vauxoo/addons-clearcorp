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
		<table width = "100%" class = "document_data">
			<tr>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>
					<span class="text_font">${check.date or ''|entity}</span>
				</td>
			</tr>
			<tr class = "detail">
				<td class = "document_data" colspan = "3">
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
		<table width = "100%" class = "document_data">
			<tr class = "part_account">
				<td>${check.narration or ''|entity}</td>
			</tr>
			%for line in check.line_cr_ids :
			<tr>
				<td>${line.account_id.code}</td>
				<td>
					${line.account_id.name}
				</td>
				<td>${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.account_id.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}</td>
				<td>${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.account_id.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}</td>
			</tr>
			%endfor
			<tr class = "check_footer">
				<td>&nbsp;</td>
				<td>&nbsp;</td>
				<td>${check.partner_id.name or ''|entity}</td>
			</tr>
		</table>
		<tr class = "zone_break"><td>&nbsp;</td><td>&nbsp;</td></tr>
	</div>
	<p style="page-break-after:always"></p>
%endfor
</body>
</html>
