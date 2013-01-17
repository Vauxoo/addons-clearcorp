<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <link rel='stylesheet' href='addons/account_webkit_report_library/webkit_headers/main.css' />
        <style>
            ${css}
        </style>
    </head>
    <body>
        <%setLang(user.context_lang)%>
        <%
            fiscalyear = get_fiscalyear(data)
            company = get_account(data)
            period_from = get_start_period(data)
            period_to = get_end_period(data)      
            sort_by = get_sortby(data)
            target_move = get_target_move(data)  
        %>
       <div class="table header">
           <div class="table-row">
               <div class="table-cell logo">${helper.embed_logo_by_name('internal_reports_logo', height=100)|n}</div>
               <br/>
               <div class="table-cell text">
                    <p class="title">${_('Journal Report ')}</p>
               </div>
           </div>
       </div>
       <div class="table list">
            <div class="table-header">
                <div class="table-row labels no-wrap">
                    <div class="table-cell first-column" style="width: 70px">${_('Chart of Accounts: ')}<br/>${company}</div>
                    <div class="table-cell" style="width: 100px">${_('Fiscal Year: ')}<br/>${fiscalyear}</div>
                    <div class="table-cell" style="width: 100px">${_('Selected period: ')}<br/> ${period_from}</div>
                    <div class="table-cell" style="width: 100px">${_('Entries Sorted By:')}<br/>${sort_by}</div>
                    <div class="table-cell last-column" style="width: 40px">${_('Target Moves: ')}<br/>${target_move}</div>
                </div>
            </div>
       </div>
       <% 
           period_id = data['form']['period_from']           
           journal_ids = data['form']['journal_ids'] 
           journal_list = get_journal_list(journal_ids)            
       %>
       %for journal in journal_list:
           <br/><br/>
           <div class="table header">
                <div class="table-row">
                   <div class="table-cell text">
                        <p class="subtitle">${journal.code +' - ' +journal.name + ' - ' + journal.company_id.currency_id.name}</p>
                   </div>
                </div>
           </div>
           <% 
              journal_move_lines = lines(period_id, journal.id)  
           %>
           <div class="table list">
                <div class="table-header">
                    <div class="table-row labels no-wrap">
                        %if display_currency(data) is False:
                            <div class="table-cell first-column" style="width: 200px">${_('Move')}</div>
                            <div class="table-cell" style="width: 100px">${_('Date')}</div>
                            <div class="table-cell" style="width: 70px">${_('Account')}</div>
                            <div class="table-cell" style="width: 300px">${_('Partner')}</div>
                            <div class="table-cell" style="width: 300px">${_('Label')}</div>
                            <div class="table-cell" style="width: 100px">${_('Debit')}</div>                    
                            <div class="table-cell last-column" style="width: 100px">${_('Credit')}</div>
                       %else:
                            <div class="table-cell first-column" style="width: 100px">${_('Move')}</div>
                            <div class="table-cell" style="width: 100px">${_('Date')}</div>
                            <div class="table-cell" style="width: 70px">${_('Account')}</div>
                            <div class="table-cell" style="width: 200px">${_('Partner')}</div>
                            <div class="table-cell" style="width: 300px">${_('Label')}</div>
                            <div class="table-cell" style="width: 100px">${_('Debit')}</div>                    
                            <div class="table-cell" style="width: 100px">${_('Credit')}</div>
                            <div class="table-cell last-column" style="width: 70px">${_('Amount Currency')}</div>
                       %endif
                    </div>
                </div>
                <div class="table-body">                    
                    %for line in journal_move_lines:
                        <div class="table-row ${row_even and 'even' or 'odd'}">
                            %if line.move_id.name:
                                <div class="table-cell first-column">${line.move_id.name} </div>
                            %else:
                                <div class="table-cell first-column">${line.move_id.id} </div>
                            %endif
                            <div class="table-cell">${formatLang(line.date,date=True)}</div>
                            <div class="table-cell">${line.account_id.code}</div>
                            <div class="table-cell">${line.partner_id.name or ''}</div>
                            <div class="table-cell">${line.name}</div>
                            <div class="table-cell amount">${formatLang(line.debit)}</div>
                             %if display_currency(data) is False:
                                <div class="table-cell amount last-column">${formatLang(line.credit)}</div>
                             %else:
                                 <div class="table-cell amount">${formatLang(line.credit)}</div>
                                 <div class="table-cell amount last-column">${get_format_lang_currency(cr, uid, formatLang(line.amount_currency), line.currency_id)}</div>
                             %endif
                       </div>
                    %endfor
                </div>
            </div>
            %if display_currency(data) is False:
                <div class="table-row subtotal">
                    <div class="table-cell first-column" style="width: 200px"></div>
                    <div class="table-cell" style="width: 100px"></div>
                    <div class="table-cell" style="width: 70px"></div>
                    <div class="table-cell" style="width: 400px"></div>
                    <div class="table-cell" style="width: 900px">${_('TOTAL')}</div>
                    <div class="table-cell amount" style="width: 100px" >${formatLang(sum_debit(period_id, journal.id))}</div>
                    <div class="table-cell amount last-column" style="width: 100px">${formatLang(sum_credit(period_id, journal.id))}</div>
                </div>
           %else:
                <div class="table-row subtotal">
                    <div class="table-cell first-column" style="width: 100px"></div>
                    <div class="table-cell" style="width: 100px"></div>
                    <div class="table-cell" style="width: 70px"></div>
                    <div class="table-cell" style="width: 200px"></div>
                    <div class="table-cell" style="width: 300px">${_('TOTAL')}</div>
                    <div class="table-cell" style="width: 100px">${formatLang(sum_debit(period_id, journal.id))}</div>                    
                    <div class="table-cell" style="width: 100px">${formatLang(sum_credit(period_id, journal.id))}</div>
                    <div class="table-cell last-column" style="width: 70px"></div>
                </div>
           %endif
        %endfor
        <p style="page-break-after:always"></p>
    </body>
</html>