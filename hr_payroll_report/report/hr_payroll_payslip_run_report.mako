<html>
    <head>
        <link rel='stylesheet' href='addons/account_webkit_report_library/webkit_headers/main.css' />
        <style>
            ${css}
        </style>
    </head>
<body class = "data">
    %for run in objects :
    <%setLang(user.lang)%>
    <%
    emp_by_dep = get_obj_by_dep(run)
    %>
        <%
        total_hn = 0.0
        total_he = 0.0
        total_fe = 0.0
        total_basic = 0.0
        total_ext = 0.0
        total_fes = 0.0
        total_gross = 0.0
        total_basic = 0.0
        total_rent = 0.0
        total_ccss = 0.0
        total_bon = 0.0
        total_net = 0.0
        total_emp = 0
        %>
        <br></br><br></br>
        <div style="font-size: 20px; font-weight: bold; text-align: center;"> ${company.partner_id.name | entity} - ${company.currency_id.name | entity}</div>
        <div style="font-size: 25px; font-weight: bold; text-align: center;"> ${_('Payroll Report')}</div>
        <div style="font-size: 20px; font-weight: bold; text-align: center;"> ${run.name}</div>
        <div style="font-size: 16px; font-weight: bold; text-align: center;">Periodo de ${run.date_start} a ${run.date_end}</div>
         </br></br>
        %for department in emp_by_dep:
            <%
            total_hn_dep = 0.0
            total_he_dep = 0.0
            total_fe_dep = 0.0
            total_basic_dep = 0.0
            total_ext_dep = 0.0
            total_fes_dep = 0.0
            total_gross_dep = 0.0
            total_basic_dep = 0.0
            total_rent_dep = 0.0
            total_ccss_dep = 0.0
            total_bon_dep = 0.0
            total_net_dep = 0.0
            total_emp_dep = 0
            %>
            <div style="font-size: 16px; font-weight: bold; text-align: left;">${department[0]}</div>
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
            
                <div class="table-body">
                    %for slip in sorted(department[1], key=lambda slip: slip.employee_id.name):
                    <div class="table-row ${row_even and 'even' or 'odd'}">
                        ## Id card
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${slip.employee_id.identification_id or ''}</div>
                        ## name
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${slip.employee_id.name or '0'}</div>
                        ## bank account
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${slip.employee_id.bank_account_id.acc_number or ' '}</div>
                        ## hn
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${get_hn(slip.worked_days_line_ids) or '0'}</div>				
                        ## he
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${get_he(slip.worked_days_line_ids) or '0'}</div>
                        ## basic
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_basic(slip.line_ids)) or '0'}</div>
                        ## ext
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_ext(slip.line_ids)) or '0'}</div>
                        ## gross
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_gross(slip.line_ids)) or '0'}</div>
                        ## ccss
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_ccss(slip.line_ids)) or '0'}</div>
                        ## bon
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_bon(slip.line_ids)) or '0'}</div>
                        ## RENT
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_rent(slip.line_ids)) or '0'}</div>
                        ## NET
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(get_net(slip.line_ids)) or '0'}</div>
                    <%
                        ## Totals by Departament
                        total_hn_dep += get_hn(slip.worked_days_line_ids)
                        total_he_dep += get_he(slip.worked_days_line_ids)
                        total_fe_dep += get_fe(slip.worked_days_line_ids)
                        total_basic_dep += get_basic(slip.line_ids)
                        total_ext_dep += get_ext(slip.line_ids)
                        total_fes_dep += get_fes(slip.line_ids)
                        total_gross_dep += get_gross(slip.line_ids)
                        total_rent_dep += get_rent(slip.line_ids)
                        total_ccss_dep += get_ccss(slip.line_ids)
                        total_bon_dep += get_bon(slip.line_ids)
                        total_net_dep += get_net(slip.line_ids)
                        total_emp_dep += 1

                        ## Totals
                        total_hn += get_hn(slip.worked_days_line_ids)
                        total_he += get_he(slip.worked_days_line_ids)
                        total_fe += get_fe(slip.worked_days_line_ids)
                        total_basic += get_basic(slip.line_ids)
                        total_ext += get_ext(slip.line_ids)
                        total_fes += get_fes(slip.line_ids)
                        total_gross += get_gross(slip.line_ids)
                        total_rent += get_rent(slip.line_ids)
                        total_ccss += get_ccss(slip.line_ids)
                        total_bon += get_bon(slip.line_ids)
                        total_net += get_net(slip.line_ids)
                        total_emp += 1
                    %>
                    </div>
                    %endfor
                </div>
                <div class="table-header">
                    <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${_('Total')}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${total_emp_dep} ${_('Employees')}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;"> </div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${total_hn_dep}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${total_he_dep}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(total_basic_dep)}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(total_ext_dep)}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(total_gross_dep)}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(total_ccss_dep)}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(total_bon_dep)}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(total_rent_dep)}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(total_net_dep)}</div>
                    </div>
                </div>
            </div>
        %endfor
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
    %endfor
</body>
</html>
