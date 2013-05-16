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
            account_list_obj, account_lines, account_conciliation, account_balance, move_names = get_data(cr, uid, data) 
        %> 
        %for account in account_list_obj:
           <%
                cumul_balance = account_balance[account.id]['balance']
                amount_total_debit = amount_total_credit = amount_total_acum = 0.0
                print_column = False
                move_lines = []
           %>
           %if account.type != 'view':
               <br/><br/>
               <div class="table header">
                    <div class="table-row">
                       <div class="table-cell text">
                            <p class="subtitle">${account.code +' - ' +account.name}</p>
                            <p class="subtitle">${_('Initial balance:')}&nbsp;&nbsp;${formatLang(cumul_balance)}
                                &nbsp;&nbsp;&nbsp;
                                ${account.id not in account_lines.keys() and _('No move lines for this account') or ''}
                            </p>                           
                       </div>
                    </div>
               </div>
               %if account.id in account_lines.keys():
                   <% move_lines = account_lines[account.id] %>                     
                       
                    <div class="table list">
                        <div class="table-header">
                            <div class="table-row labels no-wrap">                       
                                <div class="table-cell first-column" style="width: 55px">${_('Date')}</div>
                                <div class="table-cell" style="width: 55px">${_('Period')}</div>
                                <div class="table-cell" style="width: 100px">${_('Entry')}</div>
                                <div class="table-cell" style="width: 70px">${_('Journal')}</div>
                                <div class="table-cell" style="width: 100px">${_('Partner')}</div>                    
                                <div class="table-cell" style="width: 100px">${_('Label')}</div>
                                %if account.reconcile or (account.id in account_conciliation.keys() and account_conciliation[account.id]):
                                    <% print_column = True %>
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
                                    amount_total_debit += line.debit
                                    amount_total_credit += line.credit
                                    cumul_balance = cumul_balance + line.debit - line.credit                               
                                %>
                                <div class="table-row ${row_even and 'even' or 'odd'}">
                                    <div class="table-cell first-column">${formatLang(line.date, date=True)}</div>
                                    <div class="table-cell">${line.period_id.name or ''}</div>
                                    <div class="table-cell">${move_names[line.id] or ''}</div>                                    
                                    <div class="table-cell">${line.journal_id.name}</div>    
                                    <div class="table-cell">${line.partner_id.name or ''}</div>
                                    <div class="table-cell">${line.name or ''}</div> 
                                    %if print_column:
                                        <div class="table-cell">
                                            ${line.id in account_conciliation[account.id].keys() and account_conciliation[account.id][line.id] or ''}
                                        </div>
                                    %endif 
                                    <div class="table-cell amount">${formatLang(line.debit)}</div>
                                    <div class="table-cell amount">${formatLang(line.credit)}</div>                                  
                                    <div class="table-cell amount last-column">${formatLang(cumul_balance)}</div>  
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
                                %if print_column:
                                    <div class="table-cell">&nbsp;</div>
                                %endif
                                <div class="table-cell">${_('TOTAL')}</div>
                                <div class="table-cell amount" >${formatLang(amount_total_debit)}</div>
                                <div class="table-cell amount" >${formatLang(amount_total_credit)}</div>
                                <div class="table-cell amount last-column" >${formatLang(cumul_balance)}</div>
                            </div>
                            <% 
                               amount_total_debit = amount_total_credit = 0.0
                            %>
                        </div>                    
                    </div>    
                %endif                             
            %endif
        %endfor 
    </body>
</html>
