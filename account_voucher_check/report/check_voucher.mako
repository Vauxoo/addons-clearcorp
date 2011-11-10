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
			<tr class = "title">
				<td class = "document_data">
					<span class="title">${check.partner_id.name or ''|entity}</span><br/>
				<td>
					<span class="title">${(check.date or ''|entity}</span>
				</td>
				<td>
					<span class = "title">${formatLang(check.amount)}</span>
				</td>
			</tr>
		</table>
		<table width = "100%" class = "document_data">
			<tr class = "part_account">
				<td>${check.narration}</td>
			</tr>
			%for line in check.line_dr_ids :
			<tr>
				<td>${line.account_id.code}</td>
				<td>
					${line.account_id.name}
				</td>
				<td>${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.account_id.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}</td>
				<td>${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.account_id.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}</td>
			</tr>
			%endfor
		</table>
		<tr class = "zone_break"><td>&nbsp;</td><td>&nbsp;</td></tr>
	</div>
	<p style="page-break-after:always"></p>
%endfor
</body>
</html>
