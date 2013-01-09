<!DOCTYPE html SYSTEM "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <style type="text/css">
            .account_level_1 {
                text-transform: uppercase;
                font-size: 15px;
                background-color:#F0F0F0;
            }

            .account_level_2 {
                font-size: 12px;
                background-color:#F0F0F0;
            }

            .regular_account_type {
                font-weight: normal;
            }

            .view_account_type {
                font-weight: bold;
            }

            .account_level_consol {
                font-weight: normal;
                font-style: italic;
            }

            ${css}

            .list_table .act_as_row {
                margin-top: 10px;
                margin-bottom: 10px;
                font-size:10px;
            }
        </style>
    </head>
    <body class = "data">
        <%
            import copy
            
            setLang(user.context_lang)
            start_date = data['form']['date_from']
            end_date = data['form']['date_to']
            project_task_works = get_project_task_works_by_dates(cr, uid, start_date, end_date)
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
            <div style="font-size: 16px; font-weight: bold; text-align: left;">${project.complete_name or ' '}</div>
            %for project_task in project_tasks:
                <% total_hours_project_task = 0.00 %>
                %if project_task.project_id.id == project.id:
                    <div class="act_as_table list_table">
                        <div class="act_as_thead">
                            <div class="act_as_row labels" style="font-weight: bold; font-size: 11x;">
                                <div class="act_as_cell first_column" style="vertical-align: middle; text-align:center;">${_('Task Summary')}</div>
                                <div class="act_as_cell amount" style="vertical-align: middle; text-align:center;">${_('Description')}</div>
                            </div>
                        </div>
                        <div class="act_as_tbody">  
                            <div class="act_as_row lines">
                                <div class="act_as_cell">${project_task.name or ' '}</div>
                                <div class="act_as_cell">${project_task.description or ' '}</div>                    
                            </div>
                        </div>
                    </div>
                    <div class="act_as_table data_table " style="width: 500px; margin-left:auto; margin-right:auto;">
                        <div class="act_as_thead" style="align:center">
                            <div class="act_as_row lines">
                                    <div class="act_as_cell" style="text-align:center;"><b>${_('Work Summary ')}</b></div>
                                    <div class="act_as_cell" style="text-align:center;"><b>${_('Time Spent')}</b></div>
                                    <div class="act_as_cell" style="text-align:center;"><b>${_('Done by')}</b></div>
                                </div>
                            </div>
                            <div class="act_as_tbody">
                                %for project_task_work in project_task.work_ids:
                                    %if project_task_work in project_task_works:
                                        <div class="act_as_row lines">
                                            <div class="act_as_cell"style="text-align:center;">${project_task_work.name or ' '}</div>
                                            <% 
                                                hours_project_task_work = round(project_task_work.hours, 2)
                                                total_hours_project_task = total_hours_project_task + project_task_work.hours
                                                user_hours_project[project_task_work.user_id.name] = user_hours_project[project_task_work.user_id.name] + project_task_work.hours
                                                user_hours_total[project_task_work.user_id.name] = user_hours_total[project_task_work.user_id.name] + project_task_work.hours
                                            %>
                                            <div class="act_as_cell"style="text-align:center;">${hours_project_task_work or ' '}</div>                        
                                            <div class="act_as_cell"style="text-align:center;">${project_task_work.user_id.name or ' '}</div>
                                        </div>
                                    %endif
                                %endfor
                            </div> 
                        </div>
                    </div>
                    <div class="act_as_thead">
                        <div class="act_as_row labels" style="font-weight: bold; font-size: 9px;">
                            <% 
                                hours_project_task = round(total_hours_project_task, 2)
                            %>
                            <div class="act_as_cell" style="vertical-align: middle">${_('Hours Task:')} ${hours_project_task}</div>
                        </div>
                    </div>
                <% total_hours_project = total_hours_project + total_hours_project_task %>
                <br /> 
                %endif
            %endfor
            <div class="act_as_table data_table " style="width: 500px; margin-left:30%; margin-right:auto;">
                <div class="act_as_thead" style="align:center">
                    <div class="act_as_row lines">
                        <div class="act_as_cell" style="vertical-align: middle; font-weight: bold; font-size: 13px;">${_('HOURS PROJECT')}</div><br/>
                    </div>
                    %for key in user_hours_project.keys():
                        <div class="act_as_row lines">
                            %if user_hours_project[key] != 0.00:
                                <% 
                                    hours_project_user = round(user_hours_project[key], 2)
                                %>
                                <div class="act_as_cell" style="vertical-align: middle; font-size: 11px;">${key} ${_('Hours:')} ${hours_project_user}</div><br/>
                            %endif
                            <% user_hours_project[key] = 0.00 %>
                        </div>
                    %endfor
                    <div class="act_as_row lines">
                        <% 
                            hours_project = round(total_hours_project, 2)
                            total_hours = total_hours + total_hours_project
                        %>
                        <div class="act_as_cell" style="vertical-align: middle; font-weight: bold; font-size: 11px;">${_('Total:')} ${hours_project}</div><br/>
                    </div>
                </div>
            </div>
        %endfor
        <br/><br/>
        <div class="act_as_table data_table " style="width: 500px; margin-left:30%; margin-right:auto;">
            <div class="act_as_thead" style="align:center">
                <div class="act_as_row lines">
                    <div class="act_as_cell" style="vertical-align: middle; font-weight: bold; font-size: 13px;">${_('TOTAL HOURS')}</div><br/>
                </div>
                %for key in user_hours_total.keys():
                    <div class="act_as_row lines">
                        %if user_hours_total[key] != 0.00:
                            <% 
                                hours_total_user = round(user_hours_total[key], 2)
                            %>
                            <div class="act_as_cell" style="vertical-align: middle; font-size: 13px;">${key} ${_('Hours:')} ${hours_total_user}</div><br/>
                        %endif
                    </div>
                %endfor
                <div class="act_as_row lines">
                    <% 
                        hours_total = round(total_hours, 2)
                    %>
                    <div class="act_as_cell" style="vertical-align: middle; font-weight: bold; font-size: 13px;">${_('Total:')} ${hours_total}</div><br/>
                </div>
            </div>
        </div>
    </body>
</html> 
