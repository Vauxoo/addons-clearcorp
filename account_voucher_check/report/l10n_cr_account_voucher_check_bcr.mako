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
            %if count_text(check.amount,check.currency_id,check.partner_id.lang,check.company_id) < 50 :
            <div class = "amount_text">
                <span class="amount_desc">${get_text(check.amount,check.currency_id,check.partner_id.lang,check.company_id) or ''|entity}</span>
            </div>
            %elif count_text(check.amount,check.currency_id,check.partner_id.lang,check.company_id) > 50 and get_text(check.amount,check.currency_id,check.partner_id.lang,check.company_id) < 80:
            <div class = "amount_text">
                <span class="amount_desc_medium">${get_text(check.amount,check.currency_id,check.partner_id.lang,check.company_id) or ''|entity}</span>
            </div>
            %else :
            <div class = "amount_text">
                <span class="amount_desc_small">${get_text(check.amount,check.currency_id,check.partner_id.lang,check.company_id) or ''|entity}</span>
            </div>
            %endif
        </div>
        <div id = "accounting_data">
            <div id = "document_desc">
                <p>&nbsp;</p>
                <div class = "detail_desc">
                    %if check.name:
                    <span class = "text_font">${check.name or ''|entity}</span>
                    %endif
                    %for line in check.move_ids :
                    %if line.invoice.name:
                        <span class = "text_font">${ line.invoice.name or ''|entity}</span>
                        <span>&nbsp;</span>
                    %endif
                    %endfor
                </div>
            </div>
            </br>
            <div id = "accounts">
                <table width = "100%" id = "table_account" cellpadding = "0" cellspacing = "0">
                    <thead><tr><th>&nbsp;</th><th>&nbsp;</th><th>&nbsp;</th><th>&nbsp;</th></tr></thead>
                    <tbody>
                    %for line in check.move_ids :
                    <tr class = "account_line">
                        <td valign="middle" class = "code_cell">
                            ${line.account_id.code}
                        </td>
                        <td valign="middle" class = "account_id">
                            ${line.account_id.name}
                        </td>
                        <td valign="middle" class = "amount_acc">
                            ${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.debit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}
                        </td>
                        <td valign="middle" class = "amount_acc">
                            ${line.account_id.currency_id.symbol_prefix or ''|entity} ${formatLang(line.credit)} ${line.account_id.currency_id.symbol_suffix or ''|entity}
                        </td>
                    </tr>
                    %endfor
                    <tr>
                        <td colspan="4">&nbsp;</td>
                    </tr>
                    <tr>
                        <td class="code_cell">No. Pago: </td>
                        <td class="account_id">${check.number}</td>
                        <td colspan="2">&nbsp;</td>
                    </tr>
                    <tr>
                        <td class="code_cell">No. Cheque: </td>
                        <td class="account_id">${check.reference}</td>
                        <td colspan="2">&nbsp;</td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <p style="page-break-after:always"></p>
%endfor
</body>
</html>
