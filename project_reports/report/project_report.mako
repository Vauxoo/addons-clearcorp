<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <link rel='stylesheet' href='addons/account_webkit_report_library/webkit_headers/main.css' />
        <style>
            ${css}
        </style>
    </head>
    <body>
        <%
            import copy            
            setLang(user.lang)
            
            start_date = data['form']['date_from']
            end_date = data['form']['date_to']
            project_ids = data['form']['project_ids']
            project_task_works = get_project_task_works_by_dates(cr, uid, start_date, end_date, project_ids)
            project_tasks = get_project_tasks(cr, uid, project_task_works)
            projects = get_projects(cr, uid, project_tasks)
            user_hours_total = get_user_hours(cr, uid, project_task_works)
            user_hours_project = copy.deepcopy(user_hours_total)
            
            total_hours = 0.00
        %>
        <br></br>
        <div style="font-size: 20px; font-weight: bold; text-align: center;"> ${company.partner_id.name}</div>
        <div style="font-size: 25px; font-weight: bold; text-align: center;"> ${_('Project Report for Specific Dates')}</div>
        <div style="font-size: 20px; font-weight: bold; text-align: center;">${_('Task of dates:')} ${start_date} ${_('to')} ${end_date}</div>
        %for project in projects:
        <br></br>
            <% total_hours_project = 0.00 %>
            <div class="table-row subtotal">
                <div class="table-cell first-column" style="font-size: 25px; font-weight: bold; width:100%;">${project.shortcut_name or ' '}</div>
            </div>
            %for project_task in project_tasks:
                <% total_hours_project_task = 0.00 %>
                %if project_task.project_id.id == project.id:
                    <div class="table list">
                        <div class="table-header">
                            <div class="table-row labels no-wrap">
                                <div class="table-cell" style="width:10%;">${_('Number')}</div>
                                <div class="table-cell" style="width:35%;">${_('Task Summary')}</div>
                                <div class="table-cell" style="width:55%;">${_('Description')}</div>
                            </div>
                        </div>
                        <div class="table-body">
                            <div class="table-row ${row_even and 'even' or 'odd'}">
                                <div class="table-cell" style="width:10%; text-align:center; border:silver 1px solid;">${project_task.number or ' '}</div>
                                <div class="table-cell" style="width:35%; border:silver 1px solid;">${project_task.name or ' '}</div>
                                <div class="table-cell" style="width:55%; border:silver 1px solid;">${project_task.description or ' '}</div>                    
                            </div>
                        </div>
                    </div>
                    <div class="table list">
                        <div class="table-header">
                            <div class="table-row ${row_even and 'even' or 'odd'}">
                                    <div class="table-cell" style="width:45%; text-align:center; border:silver 1px solid;"><b>${_('Work Summary ')}</b></div>
                                    <div class="table-cell" style="width:15%; text-align:center; border:silver 1px solid;"><b>${_('Date')}</b></div>
                                    <div class="table-cell" style="width:10%; text-align:center; border:silver 1px solid;"><b>${_('Time Spent')}</b></div>
                                    <div class="table-cell" style="width:30%; text-align:center; border:silver 1px solid;"><b>${_('Done by')}</b></div>
                            </div>
                        </div>
                        <div class="table-body">
                            %for project_task_work in project_task.work_ids:
                                %if project_task_work in project_task_works:
                                    <div class="table-row ${row_even and 'even' or 'odd'}">
                                        <div class="table-cell" style="width:45%; border:silver 1px solid;">${project_task_work.name or ' '}</div>
                                        <% 
                                            datetime_project_task_work = project_task_work.date
                                            date_project_task_work_list = datetime_project_task_work.split(' ')
                                            date_project_task_work = date_project_task_work_list[0]
                                        
                                            hours_project_task_work = round(project_task_work.hours, 2)
                                            total_hours_project_task = total_hours_project_task + project_task_work.hours
                                            user_hours_project[project_task_work.user_id.name] = user_hours_project[project_task_work.user_id.name] + project_task_work.hours
                                            user_hours_total[project_task_work.user_id.name] = user_hours_total[project_task_work.user_id.name] + project_task_work.hours
                                        %>
                                        <div class="table-cell" style="width:15%; text-align:center; border:silver 1px solid;">${date_project_task_work or ' '}</div>
                                        <div class="table-cell" style="width:10%; text-align:center; border:silver 1px solid;">${hours_project_task_work or ' '}</div>                        
                                        <div class="table-cell" style="width:30%; text-align:center; border:silver 1px solid;">${project_task_work.user_id.name or ' '}</div>
                                    </div>
                                %endif
                            %endfor
                        </div> 
                    </div>
                    <div class="table-row subtotal">                                                
                        <% 
                            hours_project_task = round(total_hours_project_task, 2)
                        %>
                        <div class="table-cell first-column"><b>${_('Hours Task:')} ${hours_project_task}</b></div>
                    </div>
                    <% total_hours_project = total_hours_project + total_hours_project_task %>
                    <br /> 
                %endif
            %endfor
            <div align="center">
                <div class="table result">
                    <div class="table-row labels no-wrap">
                        <div class="table-cell">${_('HOURS PROJECT')}</div><br/>
                    </div>
                </div>
                <div class="table result">
                    %for key in user_hours_project.keys():
                        <div class="table-row labels no-wrap">
                            %if user_hours_project[key] != 0.00:
                                <% 
                                    hours_project_user = round(user_hours_project[key], 2)
                                %>
                                <div class="table-cell">${key} ${_('Hours:')} ${hours_project_user}</div><br/>
                            %endif
                            <% user_hours_project[key] = 0.00 %>
                        </div>
                    %endfor
                    <div class="table-row labels no-wrap">
                        <% 
                            hours_project = round(total_hours_project, 2)
                            total_hours = total_hours + total_hours_project
                        %>
                        <div class="table-cell"><b>${_('Total:')} ${hours_project}</b></div><br/>
                    </div>
                </div>
            </div>
        %endfor
        <br/><br/>
        <div align="center">
            <div class="table result">
                <div class="table-row labels no-wrap">
                    <div class="table-cell">${_('TOTAL HOURS')}</div><br/>
                </div>
            </div>
            %for key in user_hours_total.keys():
                <div class="table result">
                    <div class="table-row labels no-wrap">
                        %if user_hours_total[key] != 0.00:
                            <% 
                                hours_total_user = round(user_hours_total[key], 2)
                            %>
                            <div class="table-cell">${key} ${_('Hours:')} ${hours_total_user}</div><br/>
                        %endif
                    </div>
                </div>
            %endfor
            <div class="table result">
                <div class="table-row labels no-wrap">
                    <% 
                        hours_total = round(total_hours, 2)
                    %>
                    <div class="table-cell"><b>${_('Total:')} ${hours_total}</b></div><br/>
                </div>
            </div>
        </div>
    </body>
</html> 
