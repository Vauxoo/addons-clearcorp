<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <link rel='stylesheet' href='addons/account_webkit_report_library/webkit_headers/main.css' />
        <style>
            ${css}
        </style>
    </head>
    <body class = "data">
        <%setLang(user.lang)%>
        <%
        period_from = data['form']['period_from'][0]
        period_to = data['form']['period_to'][0]
        start_period = get_period_by_id(cr, uid, period_from)
        stop_period = get_period_by_id(cr, uid, period_to)
        %>
        
        <div style="font-size: 20px; font-weight: bold; text-align: center;"> ${company.partner_id.name}</div>
        <div style="font-size: 20px; font-weight: bold; text-align: center;"> ${_('Report Employee by Periods')}</div>
        <div style="font-size: 16px; font-weight: bold; text-align: center;">${_('Payslips of periods:')} ${start_period.name} ${_('to')} ${stop_period.name}</div>
        
        <%
        total_hn = 0.0
        total_he = 0.0
        total_basic = 0.0
        total_ext = 0.0
        total_gross = 0.0
        total_basic = 0.0
        total_rent = 0.0
        total_ccss = 0.0
        total_bon = 0.0
        total_net = 0.0
        total_emp = 0
        %>
        
        <div class="table list">
            <div class="table-header">
                <div class="table-row ${row_even and 'even' or 'odd'}">
                    <div class="table-cell" style="width:14%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Id card')}</div>
                    <div class="table-cell" style="width:17%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Name')}</div>
                    <div class="table-cell" style="width:13%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Bank account')}</div>
                    <div class="table-cell" style="width:6.22%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Hrs.')}<br />${_('Nor')}</div>
                    <div class="table-cell" style="width:6.22%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Hrs.')}<br />${_('Ext')}</div>
                    <div class="table-cell" style="width:6.22%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Ingr.')}<br />${_('Normal')}</div>
                    <div class="table-cell" style="width:6.22%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Ingr.')}<br />${_('Extra')}</div>
                    <div class="table-cell" style="width:6.22%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Salary')}<br />${_('Gross')}</div>
                    <div class="table-cell" style="width:6.22%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Deducc.')}<br />${_('CCSS/BP')}</div>
                    <div class="table-cell" style="width:6.22%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Bonuses')}</div>
                    <div class="table-cell" style="width:6.22%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Tax')}<br />${_('Rent')}</div>
                    <div class="table-cell" style="width:6.22%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Salary')}<br />${_('Net')}</div>
                </div>
            </div>
        
        
            <%
            payslips_by_employee = get_payslips_by_employee(cr, uid, start_period, stop_period)
            %>
        
            <div class="table-body">
            %for payslip in payslips_by_employee:
                <div class="table-row ${row_even and 'even' or 'odd'}">
                    ## Id card
                    <div class="table-cell" style="text-align:left; border:silver 1px solid;">${payslip.employee_id.identification_id or ' '}</div>
                    ## name
                    <div class="table-cell" style="text-align:left; border:silver 1px solid;">${payslip.employee_id.name or ' '}</div>
                    ## bank account
                    <div class="table-cell" style="text-align:left; border:silver 1px solid;">${payslip.employee_id.bank_account_id.acc_number or ' '}</div>
                    ## hn
                    <div class="table-cell" style="text-align:left; border:silver 1px solid;">${get_hn(cr, uid, payslip) or '0'}</div>
                    ## he
                    <div class="table-cell" style="text-align:left; border:silver 1px solid;">${get_he(cr, uid, payslip) or '0'}</div>
                    ## basic
                    <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_basic(cr, uid, payslip)) or '0'}</div>
                    ## ext
                    <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_ext(cr, uid, payslip)) or '0'}</div>
                    ## gross
                    <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_gross(cr, uid, payslip)) or '0'}</div>
                    ## ccss
                    <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_ccss(cr, uid, payslip)) or '0'}</div>
                    ## bon
                    <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_bon(cr, uid, payslip)) or '0'}</div>
                    ## RENT
                    <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_rent(cr, uid, payslip)) or '0'}</div>
                    ## NET
                    <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_net(cr, uid, payslip)) or '0'}</div>
                    <%

                    ## Totals
                    total_hn += get_hn(cr, uid, payslip)
                    total_he += get_he(cr, uid, payslip)
                    total_basic += get_basic(cr, uid, payslip)
                    total_ext += get_ext(cr, uid, payslip)
                    total_gross += get_gross(cr, uid, payslip)
                    total_rent += get_rent(cr, uid, payslip)
                    total_ccss += get_ccss(cr, uid, payslip)
                    total_bon += get_bon(cr, uid, payslip)
                    total_net += get_net(cr, uid, payslip)
                    %>
                </div>
            %endfor
            </div>
        </div>
        <div class="table list">
            <div class="table-header">
                <div class="table-row ${row_even and 'even' or 'odd'}">
                    <div class="table-cell" style="width:14%; text-align:left; border:silver 1px solid;">${_('TOTAL')}</div>
                    <div class="table-cell" style="width:17%; text-align:left; border:silver 1px solid;">${total_emp} ${_('Employees')}</div>
                    <div class="table-cell" style="width:13%; text-align:left; border:silver 1px solid;"> </div>
                    <div class="table-cell" style="width:6.22%; text-align:left; border:silver 1px solid;">${total_hn}</div>
                    <div class="table-cell" style="width:6.22%; text-align:left; border:silver 1px solid;">${total_he}</div>
                    <div class="table-cell" style="width:6.22%; text-align:left; border:silver 1px solid;">${formatLang(total_basic)}</div>
                    <div class="table-cell" style="width:6.22%; text-align:left; border:silver 1px solid;">${formatLang(total_ext)}</div>
                    <div class="table-cell" style="width:6.22%; text-align:left; border:silver 1px solid;">${formatLang(total_gross)}</div>
                    <div class="table-cell" style="width:6.22%; text-align:left; border:silver 1px solid;">${formatLang(total_ccss)}</div>
                    <div class="table-cell" style="width:6.22%; text-align:left; border:silver 1px solid;">${formatLang(total_bon)}</div>
                    <div class="table-cell" style="width:6.22%; text-align:left; border:silver 1px solid;">${formatLang(total_rent)}</div>
                    <div class="table-cell" style="width:6.22%; text-align:left; border:silver 1px solid;">${formatLang(total_net)}</div>
                </div>
            </div>
        </div>
    </body>
</html>
