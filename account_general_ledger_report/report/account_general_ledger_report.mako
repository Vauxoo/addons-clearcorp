<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <link rel='stylesheet' href='addons/account_webkit_report_library/webkit_headers/main.css' />
        <style>
            ${css}
        </style>
    </head>
    <body>
        <div class="table header">
           <div class="table-row">
               <div class="table-cell logo">${helper.embed_logo_by_name('internal_reports_logo', height=100)|n}</div>
               <br/>
               <div class="table-cell text">
                    <p class="title">${_('General Ledger Report ')}</p>
               </div>
           </div>
        </div>
        <%
            chart_account = get_chart_account_id(data)
            fiscalyear = get_fiscalyear(data)
            filter = get_filter(data)
        %>
        <div class="table list">
            <div class="table-header">
                <div class="table-row labels no-wrap">
                    <div class="table-cell first-column" style="width: 70px">${_('Chart of Accounts: ')}<br/>${chart_account.name}</div>
                    <div class="table-cell" style="width: 70px">${_('Fiscal Year: ')}<br/>${fiscalyear.name}</div>
                    <div class="table-cell" style="width: 70px">${_('Filter by: ')}<br/>
                         %if filter == 'filter_date':
                             <%
                                start_date = get_start_date(data)
                                stop_date = get_stop_date(data)
                             %>
                             ${_('Dates: ')}<br/>
                             ${formatLang(start_date, date=True) if start_date else u'' }&nbsp;-&nbsp;${formatLang(stop_date, date=True) if start_date else u'' }
                         %elif filter == 'filter_period':
                             <%
                                start_period = get_start_period(data)
                                stop_period = get_end_period(data)
                             %>
                             ${_('Period: ')}<br/>
                             ${start_period.name if start_period else u''}&nbsp;-&nbsp;${stop_period.name if stop_period else u'' }
                         %else:
                             ${_('No filter')}
                        %endif
                    </div>
                    <div class="table-cell" style="width: 70px">${_('Accounts: ')}<br/>
                         %if accounts(data):
                           %for account in accounts(data):
                                ${(account.code) + ','}<br/>
                           %endfor
                        %else:
                            ${_('All')}
                        %endif
                    </div>
                    <div class="table-cell" style="width: 70px">${_('Target moves: ')}<br/>${ display_target_move(data) }</div>
                </div>
            </div>            
        </div>
        <%
            account_lines, account_balance, account_conciliation = get_data(cr, uid, data) 
        %> 
        %for account, move_lines in account_lines.items():
           <%
                count = 1
                cumul_balance_ant = 0
                cumul_balance_ac = 0
                amount_total_debit = amount_total_credit = amount_total_acum = 0.0
           %>
           <br/><br/>
           <div class="table header">
                <div class="table-row">
                   <div class="table-cell text">
                        <p class="subtitle">${account.code +' - ' +account.name}</p>
                        <p class="subtitle">${_('Initial balance:')}&nbsp;&nbsp;${formatLang(account_balance[account.id]['balance'])}</p>
                   </div>
                </div>
           </div>
           <div class="table list">
                <div class="table-header">
                    <div class="table-row labels no-wrap">                       
                        <div class="table-cell first-column" style="width: 70px">${_('Date')}</div>
                        <div class="table-cell" style="width: 70px">${_('Period')}</div>
                        <div class="table-cell" style="width: 70px">${_('Entry')}</div>
                        <div class="table-cell" style="width: 70px">${_('Journal')}</div>
                        <div class="table-cell" style="width: 100px">${_('Partner')}</div>                    
                        <div class="table-cell" style="width: 100px">${_('Label')}</div>
                        %if len(account_conciliation) > 0:
                            <div class="table-cell" style="width: 70px">${_('Reconcile')}</div>
                        %endif
                        <div class="table-cell" style="width: 80px">${_('Debit')}</div>
                        <div class="table-cell" style="width: 80px">${_('Credit')}</div>
                        <div class="table-cell amount last-column" style="width: 80px">${_('Cumul. Bal.')}</div>                        
                    </div>
                </div>
                <div class="table-body"> 
                    %for line in move_lines:
                        <% 
                            move_names = extract_name_move(cr, uid, move_lines)
                            
                            amount_total_debit += line.debit
                            amount_total_credit += line.credit
                        %>
                        <div class="table-row ${row_even and 'even' or 'odd'}">
                            <div class="table-cell first-column" style="width: 70px">${formatLang(line.date, date=True)}</div>
                            <div class="table-cell" style="width: 70px">${line.period_id.name or ''}</div>
                            <div class="table-cell" style="width: 70px">${move_names[line.id]}</div>
                            <div class="table-cell" style="width: 70px">${line.journal_id.name}</div>    
                            <div class="table-cell" style="width: 100px">${line.partner_id.name or ''}</div>
                            <div class="table-cell" style="width: 100px">${line.name or ''}</div> 
                            %if len(account_conciliation) > 0:
                                <div class="table-cell" style="width: 70px">
                                    %if account.id in account_conciliation.keys() and line.id in account_conciliation.keys():
                                        conciliation = account_conciliation[account.id][line.id]
                                    %endif
                                 ${conciliation or ''}   
                                 </div>
                            %endif 
                            <div class="table-cell amount" style="width: 80px">${formatLang(line.debit)}</div>
                            <div class="table-cell amount" style="width: 80px">${formatLang(line.credit)}</div>  
                            %if count == 1:
                                <%                                  
                                    cumul_balance_ant = account_balance[account.id]['balance']
                                %>
                                <div class="table-cell amount last-column" style="width: 80px">${formatLang(cumul_balance_ant)}</div>  
                                <% count +=1 %>           
                            %else:
                                <%                                     
                                   cumul_balance_ac = cumul_balance_ant + line.debit - line.credit
                                   cumul_balance_ant = cumul_balance_ac
                                %>
                                 <div class="table-cell amount last-column" style="width: 80px">${formatLang(cumul_balance_ac)}</div>  
                                <% count +=1 %>
                            %endif
                            
                       </div>
                   %endfor                   
                   <div class="table-row spacer">
                        <div class="table-cell">&nbsp;</div>
                   </div>
                    <div class="table-row subtotal">
                        <div class="table-cell first-column">&nbsp;</div>
                        <div class="table-cell">&nbsp;</div>
                        <div class="table-cell">&nbsp;</div>
                        <div class="table-cell">&nbsp;</div>
                        <div class="table-cell">&nbsp;</div>
                        <div class="table-cell">&nbsp;</div>
                        <div class="table-cell">${_('TOTAL')}</div>
                        <div class="table-cell amount" >${formatLang(amount_total_debit)}</div>
                        <div class="table-cell amount" >${formatLang(amount_total_credit)}</div>
                        <div class="table-cell amount last-column" >${formatLang(cumul_balance_ac)}</div>
                    </div>
                    <% 
                       amount_total_debit = amount_total_credit = 0.0
                    %>
                </div>
            </div>     
        %endfor 
    </body>
</html>
