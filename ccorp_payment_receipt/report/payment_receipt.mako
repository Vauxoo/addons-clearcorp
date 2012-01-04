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
				<div id="number">${_("No.")}  ${check.number or ''|entity}</div>
				<div class="text_font"><span class="text_doct">${_("Date")}:</span> ${check.date or ''|entity}</div>
			</div>
			<div class = "detail">
				<span class="text_doct">${_("We recieve from")}:</span> <span class="text_font">${check.partner_id.name or ''|entity}</span>
			</div>
			<div class = "detail">
				<span class="text_doct">${_("The amount of")}:</span> <span class = "amount_text">${get_text(check.amount,check.currency_id) or ''|entity}</span>
			</div>
			<div class = "detail">
				<span class="text_doct">${_("Concept of")}:</span> <span class="text_font">${check.name or ''|entity}</span>
			</div>
			<div class = "detail">
				<span class="text_doct">${_("Observations")}:</span> <span class = "text_font"> ${check.narration or ''|entity}</span>
			</div>
		</div>
		<hr/>
		<table id = "validation">
			<tr>
				<td  class = "line">
					<hr/>
				</td>
				<td class = "payment_method">
					%if check.journal_id.type == 'cash':
						<span class = "amount">${_("Cash")}</span>
					%elif check.journal_id.type == 'bank':
						<span class="text_doct">${_("Check No.")}:</span> <span class = "amount">${check.reference or ''|entity }</span>
					%endif
				</td>
			</tr>
			<tr id = "val_second">
				<td class = "info">
					<span class = "info_detail">${_("LA VALIDEZ DE ESTE RECIBO QUEDA SUJETA A QUE LOS CHEQUES RECIBIDOS SEAN PAGADOS POR EL BANCO A NUESTRA SATISFACCION")}</span>
					<span class = "info_detail">${_("AUTORIZADO MEDIANTE OFICIO No.04-00007-97 DE FECHA 30-09-97 DE LA D.G.T.D.")}</span>
				</td>
				<td valign = "top" class = "signature">
					<span class = "sign_detail">${_("P/")} ${check.company_id.partner_id.name or ''|entity }</span>
					<span class="sign_line"><hr/></span>
				</td>
			</tr>
		</table>
	</div>
	<p style="page-break-after:always"></p>
	%endfor
</body>
</html>
