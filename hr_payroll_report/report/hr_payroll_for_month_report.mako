<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style>
            ${css}
            .body {
                width: 1650px !important;
            }
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
        <div style="font-size: 25px; font-weight: bold; text-align: center;"> ${_('Payroll Report for Specific Periods')}</div>
        <div style="font-size: 16px; font-weight: bold; text-align: center;">${_('Payslips of periods:')} ${start_period.name} ${_('to')} ${stop_period.name}</div>
        
        <%
        payslips_by_struct = get_payslips_by_struct(cr, uid, start_period, stop_period)

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

        %for struct in payslips_by_struct:
            <%
            total_hn_struct = 0.0
            total_he_struct = 0.0
            total_ext_struct = 0.0
            total_gross_struct = 0.0
            total_basic_struct = 0.0
            total_rent_struct = 0.0
            total_ccss_struct = 0.0
            total_bon_struct = 0.0
            total_net_struct = 0.0
            total_emp_struct = 0

            %>
            
            </br>
            <div style="font-size: 16px; font-weight: bold; text-align: left;">${struct[0]}</div>
            <div class="table list">
                <div class="table-header">
                    <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="width:11%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Id card')}</div>
                        <div class="table-cell" style="width:16%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Name')}</div>
                        <div class="table-cell" style="width:11%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Bank account')}</div>
                        <div class="table-cell" style="width:3%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Hrs.')}<br />${_('Nor')}</div>
                        <div class="table-cell" style="width:3%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Hrs.')}<br />${_('Ext')}</div>
                        <div class="table-cell" style="width:8%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Ingr.')}<br />${_('Normal')}</div>
                        <div class="table-cell" style="width:8%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Ingr.')}<br />${_('Extra')}</div>
                        <div class="table-cell" style="width:8%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Salary')}<br />${_('Gross')}</div>
                        <div class="table-cell" style="width:8%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Deducc.')}<br />${_('CCSS/BP')}</div>
                        <div class="table-cell" style="width:8%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Bonuses')}</div>
                        <div class="table-cell" style="width:8%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Tax')}<br />${_('Rent')}</div>
                        <div class="table-cell" style="width:8%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Salary')}<br />${_('Net')}</div>
                    </div>
                </div>
            
            
                <%
                payslips_by_employee = get_payslips_by_employee(cr, uid, struct[1])
                %>
            
                <div class="table-body">
                %for payslips in payslips_by_employee:
                    <div class="table-row ${row_even and 'even' or 'odd'}">
                        ## Id card
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${get_identification(cr, uid, payslips[1]) or ' '}</div>
                        ## name
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${payslips[0] or ' '}</div>
                        ## bank account
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${get_bank_account(cr, uid, payslips[1]) or ' '}</div>
                        ## hn
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${get_hn(cr, uid, payslips[1]) or '0'}</div>
                        ## he
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${get_he(cr, uid, payslips[1]) or '0'}</div>
                        ## basic
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_basic(cr, uid, payslips[1])) or '0'}</div>
                        ## ext
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_ext(cr, uid, payslips[1])) or '0'}</div>
                        ## gross
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_gross(cr, uid, payslips[1])) or '0'}</div>
                        ## ccss
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_ccss(cr, uid, payslips[1])) or '0'}</div>
                        ## bon
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_bon(cr, uid, payslips[1])) or '0'}</div>
                        ## RENT
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_rent(cr, uid, payslips[1])) or '0'}</div>
                        ## NET
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_net(cr, uid, payslips[1])) or '0'}</div>
                        <%
                        ## Totals by Departament
                        total_hn_struct += get_hn(cr, uid, payslips[1])
                        total_he_struct += get_he(cr, uid, payslips[1])
                        total_basic_struct += get_basic(cr, uid, payslips[1])
                        total_ext_struct += get_ext(cr, uid, payslips[1])
                        total_gross_struct += get_gross(cr, uid, payslips[1])
                        total_rent_struct += get_rent(cr, uid, payslips[1])
                        total_ccss_struct += get_ccss(cr, uid, payslips[1])
                        total_bon_struct += get_bon(cr, uid, payslips[1])
                        total_net_struct += get_net(cr, uid, payslips[1])
                        total_emp_struct += 1

                        ## Totals
                        total_hn += get_hn(cr, uid, payslips[1])
                        total_he += get_he(cr, uid, payslips[1])
                        total_basic += get_basic(cr, uid, payslips[1])
                        total_ext += get_ext(cr, uid, payslips[1])
                        total_gross += get_gross(cr, uid, payslips[1])
                        total_rent += get_rent(cr, uid, payslips[1])
                        total_ccss += get_ccss(cr, uid, payslips[1])
                        total_bon += get_bon(cr, uid, payslips[1])
                        total_net += get_net(cr, uid, payslips[1])
                        total_emp += 1
                        %>
                    </div>
                %endfor
                </div>
                <div class="table-header">
                    <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${_('Total')}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${total_emp_struct} ${_('Employees')}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;"> </div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${total_hn_struct}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${total_he_struct}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(total_basic_struct)}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(total_ext_struct)}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(total_gross_struct)}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(total_ccss_struct)}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(total_bon_struct)}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(total_rent_struct)}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(total_net_struct)}</div>
                    </div>
                </div>
            </div>
        %endfor
        </br>
        <div class="table list">
            <div class="table-header">
                <div class="table-row ${row_even and 'even' or 'odd'}">
                    <div class="table-cell" style="width:27%; border:none;"></div>
                    <div class="table-cell" style="width:11%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;"></div>
                    <div class="table-cell" style="width:3%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Hrs.')}<br />${_('Nor')}</div>
                    <div class="table-cell" style="width:3%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Hrs.')}<br />${_('Ext')}</div>
                    <div class="table-cell" style="width:8%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Ingr.')}<br />${_('Normal')}</div>
                    <div class="table-cell" style="width:8%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Ingr.')}<br />${_('Extra')}</div>
                    <div class="table-cell" style="width:8%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Salary')}<br />${_('Gross')}</div>
                    <div class="table-cell" style="width:8%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Deducc.')}<br />${_('CCSS/BP')}</div>
                    <div class="table-cell" style="width:8%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Bonuses')}</div>
                    <div class="table-cell" style="width:8%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Tax')}<br />${_('Rent')}</div>
                    <div class="table-cell" style="width:8%; background-color:white; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Salary')}<br />${_('Net')}</div>
                </div>
            </div>
            <div class="table-header">
                <div class="table-row ${row_even and 'even' or 'odd'}">
                    <div class="table-cell" style="width:27%; border:none;"></div>
                    <div class="table-cell" style="width:11%; text-align:right; font-weight: bold; border:silver 1px solid;">${_('TOTAL')}</div>
                    <div class="table-cell" style="width:3%; text-align:left; border:silver 1px solid;">${total_hn}</div>
                    <div class="table-cell" style="width:3%; text-align:left; border:silver 1px solid;">${total_he}</div>
                    <div class="table-cell" style="width:8%; text-align:left; border:silver 1px solid;">${formatLang(total_basic)}</div>
                    <div class="table-cell" style="width:8%; text-align:left; border:silver 1px solid;">${formatLang(total_ext)}</div>
                    <div class="table-cell" style="width:8%; text-align:left; border:silver 1px solid;">${formatLang(total_gross)}</div>
                    <div class="table-cell" style="width:8%; text-align:left; border:silver 1px solid;">${formatLang(total_ccss)}</div>
                    <div class="table-cell" style="width:8%; text-align:left; border:silver 1px solid;">${formatLang(total_bon)}</div>
                    <div class="table-cell" style="width:8%; text-align:left; border:silver 1px solid;">${formatLang(total_rent)}</div>
                    <div class="table-cell" style="width:8%; text-align:left; border:silver 1px solid;">${formatLang(total_net)}</div>
                </div>
            </div>
        </div>
        <div class="table list">
            <div class="table-body">
                <div class="table-row ${row_even and 'even' or 'odd'}">
                    <br /><br />
                    <div style="font-size: 16px; font-weight: bold; text-align: left;"> ${_('BY:')} </div>
                    <div style="font-size: 16px; font-weight: bold; text-align: left;"> ${_('REVIEWED BY:')} </div>
                    <div style="font-size: 16px; font-weight: bold; text-align: left;"> ${_('APPROVED BY:')} </div>
                </div>
            </div>
        </div>   
        <p style="page-break-after:always"></p>
    </body>
</html>
