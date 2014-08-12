<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <link rel='stylesheet' href='addons/account_webkit_report_library/webkit_headers/main.css' />
        <style>
            ${css}
        </style>
    </head>
    <body>
        <%setLang(user.lang)%>       
        %for payslip in objects :
            <br></br><br></br>
            <div style="font-size: 20px; font-weight: bold; text-align: center;"> ${company.partner_id.name | entity} - ${company.currency_id.name | entity}</div>
            <div style="font-size: 25px; font-weight: bold; text-align: center;"> Comprobante de Pago de Salario</div>
            <div style="font-size: 20px; font-weight: bold; text-align: center;"> ${payslip.name or payslip.employee_id.name}</div>
            <br></br>        
            <div class="table list" style="width: 70%; margin-left: auto; margin-right: auto;">
                <div class="table-body">
                    <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;"><b>${_('Name')}</b></div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;">${payslip.employee_id.name or '-'}</div>
                   </div>
                   <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;"><b>${_('ID card')}</b></div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;">${payslip.employee_id.ssnid or '-'}</div>  
                   </div>    
                   <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;"><b>${_('Bank account')}</b></div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;">${payslip.employee_id.bank_account_id.name or '-'}</div> 
                   </div>     
                   <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;"><b>${_('Job')}</b></div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;">${payslip.contract_id.job_id.name or '-'}</div>
                   </div>                       
                   <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;"><b>${_('Reference')}</b></div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;">${payslip.number or '-'}</div>
                   </div>   
                   <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;"><b>${_('Date from')}</b></div>  
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;">${payslip.date_from or '-'}</div>
                   </div>    
                   <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;"><b>${_('Date to')}</b></div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;">${payslip.date_to or '-'}</div>
                   </div>     
                   <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;"><b>${_('Salary structure')}</b></div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;" style="text-align:left; border:silver 1px solid;">${payslip.struct_id.name or '-'}</div>
                    </div>
                </div>   
            </div>        
            <br></br>
            ##Worked days
            <% worked_lines_ids = get_worked_lines(cr,uid,payslip.id,payslip.contract_id.schedule_pay) %>
            <div style="font-size: 16px; font-weight: bold; text-align: left;"> ${_('Quantity of hours')} </div>
            <div class="table list">
                <div class="table-header">
                    <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="width:55%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Name')}</div>
                        <div class="table-cell" style="width:15%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Code')}</div>
                        <div class="table-cell" style="width:15%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Number of days')}</div>
                        <div class="table-cell" style="width:15%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Number of hours')}</div>
                    </div>
                </div>
                <div class="table-body">  
                    <% flag_HE = not_HE(cr,uid,worked_lines_ids) %>
                    <% flag_HN = not_HN(cr,uid,worked_lines_ids) %>
                    
                    %for line in worked_lines_ids:
                    <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${line.name or '-'}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${line.code or '-'}</div>                    
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(line.number_of_days) or '-'}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(line.number_of_hours) or '-'}</div>
                    </div>
                    %endfor
                    %if flag_HE is False:
                        <div class="table-row ${row_even and 'even' or 'odd'}">
                            <div class="table-cell" style="text-align:left; border:silver 1px solid;">${_('DONT EXIST EXTRA HOURS REGISTRED')}</div>
                            <div class="table-cell" style="text-align:left; border:silver 1px solid;">${'HE'}</div>                    
                            <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(0) or '-'}</div>
                            <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(0) or '-'}</div>
                        </div>
                    %endif
                    %if flag_HN is False:
                        <div class="table-row ${row_even and 'even' or 'odd'}">
                            <div class="table-cell" style="text-align:left; border:silver 1px solid;">${_('DONT EXIST NORMAL HOURS REGISTRED')}</div>
                            <div class="table-cell" style="text-align:left; border:silver 1px solid;">${'HN'}</div>                    
                            <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(0) or '-'}</div>
                            <div class="table-cell" style="text-align:left; border:silver 1px solid;">${formatLang(0) or '-'}</div>
                        </div>
                    %endif
                </div> 
            </div>
            <br></br>
            ##Salary Computation
            <div style="font-size: 16px; font-weight: bold; text-align: left;">${_('Salary Computation')} </div>
            <div class="table list">
                <div class="table-header">
                    <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="width:25%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Name')}</div>
                        <div class="table-cell" style="width:15%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Code')}</div>
                        <div class="table-cell" style="width:20%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Category')}</div>
                        <div class="table-cell" style="width:10%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Base')}</div>
                        <div class="table-cell" style="width:15%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Amount')}</div>
                        <div class="table-cell" style="width:15%; background-color:silver; font-weight: bold; text-align:center; border:silver 1px solid;">${_('Total')}</div>
                    </div>
                </div>
                <div class="table-body">
                    <% payslip_lines = get_payslip_lines(cr,uid,payslip.id) %>
                    %for line in payslip_lines:
                    <div class="table-row ${row_even and 'even' or 'odd'}">
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${line.name or '-'}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${line.code or '-'}</div>                    
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${line.category_id.name or '-'}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${line.quantity or '-'}</div>                        
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${company.currency_id.symbol}${formatLang(line.amount) or '-'}</div>
                        <div class="table-cell" style="text-align:left; border:silver 1px solid;">${company.currency_id.symbol}${formatLang(line.total) or '-'}</div>
                    </div>
                    %endfor
                </div>  
            </div>    
            <br></br> <br></br>
            <div class="table list" style="margin-top:30px">
                <div class="table-body">            
                    <div class="table-row" style="vertical-align: bottom">
                       <div style="padding-bottom:5px">___________________________________________________________</div>
                    </div>
                    <div class="table-row" style="vertical-align: bottom">
                        <div style="padding-bottom:5px"> ${_('Received and accepted: ')}${payslip.employee_id.name or ''}</div>
                    </div>
                    <div class="table-row" style="vertical-align: bottom">
                        <div style="padding-bottom:5px">${_('ID card: ')}${payslip.employee_id.ssnid or ''}</div>
                    </div>
                    <br></br> <br></br><br></br>
                    <div class="table-row" style="text-align:justify;text-justify:inter-word;">
                        <div style="padding-bottom:5px">${company.payslip_footer or ''}</div>
                    </div>
                </div>
            </div>
            <p style="page-break-after:always"></p>
        %endfor   
    </body>
</html>           
