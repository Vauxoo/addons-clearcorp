# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Addons modules by CLEARCORP S.A.
#    Copyright (C) 2009-TODAY CLEARCORP S.A. (<http://clearcorp.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from datetime import date,datetime
from openerp import models, fields, api, _
from openerp.tools.translate import _
import time
from openerp.exceptions import Warning

class IssueInvoiceWizard(models.TransientModel):
    _name='project.issue.helpdesk.invoice.wizard'
    @api.multi
    def create_invoice_lines_expenses(self,issue,is_warranty,total_expenses,product_expense,count_lines,limit_lines,invoice_dict,invoices_list,inv):
        #Method for invoice each expenses lines included in issue, the lines are grouped into a single line expenses.
        #Exchange currency rates, based in parter settings of invoice
        invoice_obj=self.env['account.invoice']
        for expense_line in issue.expense_line_ids:
            #Only invoice lines with checkbox billable, in state done or paid
            if expense_line.billable==True and (expense_line.expense_id.state=='done' or expense_line.expense_id.state=='paid'):
                for move_lines in expense_line.expense_id.account_move_id.line_id:
                    for lines in move_lines.analytic_lines:
                        if lines.account_id==expense_line.analytic_account and lines.name==expense_line.name and lines.unit_amount==expense_line.unit_quantity and (lines.amount*-1/lines.unit_amount)==expense_line.unit_amount and not lines.invoice_id:
                            factor = self.env['hr_timesheet_invoice.factor'].browse(lines.to_invoice.id)
                            #If not is warranty, the invoice lines use the customer partner settings
                            if is_warranty==False:
                                if issue.partner_id and issue.branch_id:
                                    if issue.branch_id.property_product_pricelist:
                                        if expense_line.expense_id.currency_id.id != issue.branch_id.property_product_pricelist.currency_id.id:
                                            import_currency_rate=expense_line.expense_id.currency_id.get_exchange_rate(issue.branch_id.property_product_pricelist.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                                        else:
                                            import_currency_rate = 1
                                    else:
                                        if expense_line.expense_id.currency_id.id != lines.account_id.company_id.currency_id.id:
                                            import_currency_rate=expense_line.expense_id.currency_id.get_exchange_rate(lines.account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                                        else:
                                            import_currency_rate = 1
                                elif issue.partner_id and not issue.branch_id:
                                    if issue.partner_id.property_product_pricelist:
                                        if expense_line.expense_id.currency_id.id != issue.partner_id.property_product_pricelist.currency_id.id:
                                            import_currency_rate=expense_line.expense_id.currency_id.get_exchange_rate(issue.partner_id.property_product_pricelist.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                                        else:
                                            import_currency_rate = 1
                                    else:
                                        if expense_line.expense_id.currency_id != lines.account_id.company_id.currency_id.id:
                                            import_currency_rate=expense_line.expense_id.currency_id.get_exchange_rate(lines.account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                                        else:
                                            import_currency_rate = 1
                            #If is warranty, the invoice lines use the manufacturer partner settings of product associated to issue
                            elif is_warranty==True:
                                if  issue.product_id.manufacturer.property_product_pricelist_purchase:
                                    if expense_line.expense_id.currency_id.id != issue.product_id.manufacturer.property_product_pricelist_purchase.currency_id.id:
                                        import_currency_rate=expense_line.expense_id.currency_id.get_exchange_rate(issue.product_id.manufacturer.property_product_pricelist_purchase.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                                    else:
                                        import_currency_rate = 1
                                else:
                                    if expense_line.expense_id.currency_id.id != lines.account_id.company_id.currency_id.id:
                                        import_currency_rate=expense_line.expense_id.currency_id.get_exchange_rate(lines.account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                                    else:
                                        import_currency_rate = 1
                            account_exp=lines.product_id.property_account_income.id or lines.product_id.categ_id.property_account_income_categ.id
                            total_expenses+=((lines.amount*-1)*import_currency_rate)*(100-factor.factor or 0.0) / 100.0
                            if product_expense==False:
                                product_expense=lines.product_id.id
                                taxes_expenses=[(6, 0, [tax.id for tax in lines.product_id.taxes_id])]
                            lines.write({'invoice_id':inv.id})
        if total_expenses>0:
            #Add line to invoice, included the line of expenses
            invoice_line={
                          'product_id':product_expense,
                          'name': _('Expenses of Issue #') + issue.issue_number,
                          'real_quantity':1,
                          'quantity':1,
                          'price_unit':total_expenses,
                          'invoice_line_tax_id':taxes_expenses,
                          'account_id':account_exp,
                          'account_analytic_id':issue.analytic_account_id.id
                          }
            #If Warranty is seller, the line invoices to customer included prices in zero
            if issue.warranty=='seller':
                invoice_line['price_unit']=0
            #Condition for determine if the invoice doesn't exceed the limit of lines, if is exceed a new invoice should be generated
            if count_lines<=limit_lines or limit_lines==0 or limit_lines==-1:
                if issue.issue_number not in inv.origin:
                    inv.write({'origin':inv.origin + issue.issue_number +'-'})
                inv.write({'invoice_line':[(0,0,invoice_line)]})
                inv.write({'issue_ids':[(4,issue.id)]})
                count_lines+=1
            else:
                if issue.issue_number not in inv.origin:
                    inv.write({'origin':inv.origin + issue.issue_number})
                inv=invoice_obj.create(invoice_dict)
                invoices_list.append(inv.id)
                count_lines=1
                if issue.issue_number not in inv.origin:
                    inv.write({'origin':inv.origin + issue.issue_number +'-'})
                inv.write({'invoice_line':[(0,0,invoice_line)]})
                inv.write({'issue_ids':[(4,issue.id)]})
                count_lines+=1
            total_expenses=0
        return count_lines,inv or False,invoices_list
    
    @api.multi
    def create_invoice_lines_additional_costs(self,issue,count_lines,limit_lines,is_warranty,inv,invoice_dict,invoices_list):
        #Method for invoice each additional costs lines included in issue
        #Exchange currency rates, based in parter settings of invoice
        invoice_obj=self.env['account.invoice']
        for additional_cost in issue.additional_cost_ids:
            #If not is warranty, the invoice lines use the customer partner settings
            if is_warranty==False:
                if issue.partner_id and issue.branch_id:
                    if issue.branch_id.property_product_pricelist:
                        if additional_cost.currency_id.id != issue.branch_id.property_product_pricelist.currency_id.id:
                            import_currency_rate=additional_cost.currency_id.get_exchange_rate(issue.branch_id.property_product_pricelist.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                        else:
                            import_currency_rate = 1
                    else:
                        if additional_cost.currency_id.id !=  issue.analytic_account_id.company_id.currency_id.id:
                            import_currency_rate=additional_cost.currency_id.get_exchange_rate(issue.analytic_account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                        else:
                            import_currency_rate = 1
                elif issue.partner_id and not issue.branch_id:
                    if issue.partner_id.property_product_pricelist:
                        if additional_cost.currency_id.id != issue.partner_id.property_product_pricelist.currency_id.id:
                            import_currency_rate=additional_cost.currency_id.get_exchange_rate(issue.partner_id.property_product_pricelist.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                        else:
                            import_currency_rate = 1
                    else:
                        if additional_cost.currency_id.id !=  issue.analytic_account_id.company_id.currency_id.id:
                            import_currency_rate=additional_cost.currency_id.get_exchange_rate(issue.analytic_account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                        else:
                            import_currency_rate = 1
            #If is warranty, the invoice lines use the manufacturer partner settings of product associated to issue
            elif is_warranty==True:
                if issue.partner_id and issue.branch_id:
                    if  issue.product_id.manufacturer.property_product_pricelist_purchase:
                        if additional_cost.currency_id.id != issue.product_id.manufacturer.property_product_pricelist_purchase.currency_id.id:
                            import_currency_rate=additional_cost.currency_id.get_exchange_rate(issue.product_id.manufacturer.property_product_pricelist_purchase.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                        else:
                            import_currency_rate = 1
                    else:
                        if additional_cost.currency_id.id !=issue.analytic_account_id.company_id.currency_id.id:
                            import_currency_rate=additional_cost.currency_id.get_exchange_rate(issue.analytic_account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                        else:
                            import_currency_rate = 1
                elif issue.partner_id and not issue.branch_id:
                    if  issue.product_id.manufacturer.property_product_pricelist_purchase:
                        if additional_cost.currency_id.id != issue.product_id.manufacturer.property_product_pricelist_purchase.currency_id.id:
                            import_currency_rate=additional_cost.currency_id.get_exchange_rate(issue.product_id.manufacturer.property_product_pricelist_purchase.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                        else:
                            import_currency_rate = 1
                    else:
                        if additional_cost.currency_id.id !=issue.analytic_account_id.company_id.currency_id.id:
                            import_currency_rate=additional_cost.currency_id.get_exchange_rate(issue.analytic_account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                        else:
                            import_currency_rate = 1
            #Add line to invoice, included the line of additional cost
            invoice_line={
                    'product_id':additional_cost.product_id.id or False,
                    'name':additional_cost.name or additional_cost.product_id.description or False,
                    'quantity':1,
                    'real_quantity':1,
                    'uos_id':additional_cost.product_id.uos_id.id or False,
                    'price_unit':additional_cost.price_amount*import_currency_rate,
                    'invoice_line_tax_id':[(6, 0, [tax.id for tax in additional_cost.product_id.taxes_id])],
                    'account_analytic_id':issue.analytic_account_id.id,
                    'account_id':additional_cost.product_id.property_account_income.id or additional_cost.product_id.categ_id.property_account_income_categ.id or issue.product_id.property_account_income.id or issue.product_id.categ_id.property_account_income_categ.id
                            }
            #If Warranty is seller, the line invoices to customer included prices in zero
            if issue.warranty=='seller':
                invoice_line['price_unit']=0
            #Condition for determine if the invoice doesn't exceed the limit of lines, if is exceed a new invoice should be generated
            if count_lines<=limit_lines or limit_lines==0 or limit_lines==-1:
                if issue.issue_number not in inv.origin:
                    inv.write({'origin':inv.origin + issue.issue_number +'-'})
                inv.write({'invoice_line':[(0,0,invoice_line)]})
                inv.write({'issue_ids':[(4,issue.id)]})
                count_lines+=1
            else:
                if issue.issue_number not in inv.origin:
                    inv.write({'origin':inv.origin + issue.issue_number})
                inv=invoice_obj.create(invoice_dict)
                invoices_list.append(inv.id)
                count_lines=1
                if issue.issue_number not in inv.origin:
                    inv.write({'origin':inv.origin + issue.issue_number +'-'})
                inv.write({'invoice_line':[(0,0,invoice_line)]})
                inv.write({'issue_ids':[(4,issue.id)]})
                count_lines+=1
        return count_lines,inv or False,invoices_list

    @api.multi
    def create_invoice_lines_supplier_invoices(self,issue,is_warranty,line_detailed,first_line_product,invoice_dict,invoices_list,count_lines_products,limit_lines,count_lines,inv,inv_prod):
        #Method for invoice each supplier lines invoice included in issue
        #Exchange currency rates, based in parter settings of invoice
        invoice_obj=self.env['account.invoice']
        for invoice_lines in issue.account_invoice_line_ids:
            #Only invoice lines with checkbox billable, in state open or paid
            if invoice_lines.invoice_id.state in ('open','paid') and invoice_lines.billable==True:
                #If not is warranty, the invoice lines use the customer partner settings
                if is_warranty==False:
                    if issue.partner_id and issue.branch_id:
                        if issue.branch_id.property_product_pricelist:
                            if invoice_lines.invoice_id.currency_id.id != issue.branch_id.property_product_pricelist.currency_id.id:
                                import_currency_rate=invoice_lines.invoice_id.currency_id.get_exchange_rate(issue.branch_id.property_product_pricelist.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                            else:
                                import_currency_rate = 1
                        else:
                            if invoice_lines.invoice_id.currency_id.id !=  issue.analytic_account_id.company_id.currency_id.id:
                                import_currency_rate=invoice_lines.invoice_id.currency_id.get_exchange_rate(issue.analytic_account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                            else:
                                import_currency_rate = 1
                    elif issue.partner_id and not issue.branch_id:
                        if issue.partner_id.property_product_pricelist:
                            if invoice_lines.invoice_id.currency_id.id != issue.partner_id.property_product_pricelist.currency_id.id:
                                import_currency_rate=invoice_lines.invoice_id.currency_id.get_exchange_rate(issue.partner_id.property_product_pricelist.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                            else:
                                import_currency_rate = 1
                        else:
                            if invoice_lines.invoice_id.currency_id.id !=  issue.analytic_account_id.company_id.currency_id.id:
                                import_currency_rate=invoice_lines.invoice_id.currency_id.get_exchange_rate(issue.analytic_account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                            else:
                                import_currency_rate = 1
                #If is warranty, the invoice lines use the manufacturer partner settings of product associated to issue
                elif is_warranty==True:
                    if issue.product_id.manufacturer.property_product_pricelist_purchase:
                        if invoice_lines.invoice_id.currency_id.id != issue.product_id.manufacturer.property_product_pricelist_purchase.currency_id.id:
                            import_currency_rate=invoice_lines.invoice_id.currency_id.get_exchange_rate(issue.product_id.manufacturer.property_product_pricelist_purchase.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                        else:
                            import_currency_rate = 1
                    else:
                        if invoice_lines.invoice_id.currency_id.id !=issue.analytic_account_id.company_id.currency_id.id:
                            import_currency_rate=invoice_lines.invoice_id.currency_id.get_exchange_rate(issue.analytic_account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                        else:
                            import_currency_rate = 1
                #Add line to invoice, included the line of supplier invoice line
                invoice_line={
                              'product_id':invoice_lines.product_id.id or False,
                              'name': issue.product_id.description +'-'+ invoice_lines.name,
                              'quantity':invoice_lines.quantity,
                              'real_quantity':invoice_lines.quantity,
                              'uos_id':invoice_lines.uos_id.id or False,
                              'price_unit':invoice_lines.price_unit*import_currency_rate,
                              'discount':invoice_lines.discount,
                              'invoice_line_tax_id':[(6, 0, [tax.id for tax in invoice_lines.product_id.taxes_id])],
                              'account_analytic_id':issue.analytic_account_id.id,
                              'account_id':invoice_lines.product_id.property_account_income.id or invoice_lines.product_id.categ_id.property_account_income_categ.id or issue.product_id.property_account_income.id or issue.product_id.categ_id.property_account_income_categ.id
                                    }
                #If Warranty is seller, the line invoices to customer included prices in zero
                if issue.warranty=='seller':
                    invoice_line['price_unit']=0
                #If lines detail, the invoice of products should be different to invoice services
                if line_detailed==True:
                    if first_line_product==0:
                        inv_prod=invoice_obj.create(invoice_dict)
                        if issue.issue_number not in inv_prod.origin:
                            inv_prod.write({'origin':inv_prod.origin + issue.issue_number +'-'})
                        invoices_list.append(inv_prod.id)
                        first_line_product+=1
                    #Condition for determine if the invoice doesn't exceed the limit of lines of products, if is exceed a new invoice should be generated
                    if count_lines_products<=limit_lines or limit_lines==0 or limit_lines==-1:
                        if issue.issue_number not in inv_prod.origin:
                            inv_prod.write({'origin':inv_prod.origin + issue.issue_number +'-'})
                        inv_prod.write({'invoice_line':[(0,0,invoice_line)]})
                        inv_prod.write({'issue_ids':[(4,issue.id)]})
                        count_lines_products+=1
                    else:
                        if issue.issue_number not in inv_prod.origin:
                            inv_prod.write({'origin':inv_prod.origin + issue.issue_number})
                        inv_prod=invoice_obj.create(invoice_dict)
                        invoices_list.append(inv_prod.id)
                        count_lines_products=0
                        if issue.issue_number not in inv_prod.origin:
                            inv_prod.write({'origin':inv_prod.origin + issue.issue_number +'-'})
                        inv_prod.write({'invoice_line':[(0,0,invoice_line)]})
                        inv_prod.write({'issue_ids':[(4,issue.id)]})
                        count_lines_products+=1
                else:
                    inv_prod=False
                    #Condition for determine if the invoice doesn't exceed the limit of lines, if is exceed a new invoice should be generated
                    if count_lines<=limit_lines or limit_lines==0 or limit_lines==-1:
                        if issue.issue_number not in inv.origin:
                            inv.write({'origin':inv.origin + issue.issue_number +'-'})
                        inv.write({'invoice_line':[(0,0,invoice_line)]})
                        inv.write({'issue_ids':[(4,issue.id)]})
                        count_lines+=1
                    else:
                        if issue.issue_number not in inv.origin:
                            inv.write({'origin':inv.origin + issue.issue_number})
                        inv=invoice_obj.create(invoice_dict)
                        invoices_list.append(inv.id)
                        count_lines=1
                        if issue.issue_number not in inv.origin:
                            inv.write({'origin':inv.origin + issue.issue_number +'-'})
                        inv.write({'invoice_line':[(0,0,invoice_line)]})
                        inv.write({'issue_ids':[(4,issue.id)]})
                        count_lines+=1
        return count_lines,inv or False,count_lines_products,invoices_list,first_line_product,count_lines_products,inv_prod
    @api.multi
    def create_invoice_lines_backorders(self,issue,count_lines,limit_lines,line_detailed,first_line_product,count_lines_products,is_warranty,inv,invoice_dict,invoices_list,inv_prod):
        #Method for invoice each delivery note line included in issue
        #Exchange currency rates, based in parter settings of invoice
        invoice_obj=self.env['account.invoice']
        for backorder in issue.backorder_ids:
            #Only invoice lines with state done, when the picking is type outgoing
            if backorder.delivery_note_id and backorder.delivery_note_id.state=='done' and backorder.picking_type_id.code=='outgoing' and backorder.invoice_state!='invoiced' and backorder.state=='done':
                for delivery_note_lines in backorder.delivery_note_id.note_lines:
                    #If not is warranty, the invoice lines use the customer partner settings
                    if is_warranty==False:
                        if issue.partner_id and issue.branch_id:
                            if issue.branch_id.property_product_pricelist:
                                if delivery_note_lines.note_id.currency_id.id != issue.branch_id.property_product_pricelist.currency_id.id:
                                    import_currency_rate=delivery_note_lines.note_id.currency_id.get_exchange_rate(issue.branch_id.property_product_pricelist.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                                else:
                                    import_currency_rate = 1
                            else:
                                if delivery_note_lines.note_id.currency_id.id !=  issue.analytic_account_id.company_id.currency_id.id:
                                    import_currency_rate=delivery_note_lines.note_id.currency_id.get_exchange_rate(issue.analytic_account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                                else:
                                    import_currency_rate = 1
                        elif issue.partner_id and not issue.branch_id:
                            if issue.partner_id.property_product_pricelist:
                                if delivery_note_lines.note_id.currency_id.id != issue.partner_id.property_product_pricelist.currency_id.id:
                                    import_currency_rate=delivery_note_lines.note_id.currency_id.get_exchange_rate(issue.partner_id.property_product_pricelist.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                                else:
                                    import_currency_rate = 1
                            else:
                                if delivery_note_lines.note_id.currency_id.id !=  issue.analytic_account_id.company_id.currency_id.id:
                                    import_currency_rate=delivery_note_lines.note_id.currency_id.get_exchange_rate(issue.analytic_account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                                else:
                                    import_currency_rate = 1
                    #If Warranty is seller, the line invoices to customer included prices in zero
                    elif is_warranty==True:
                        if  issue.product_id.manufacturer.property_product_pricelist_purchase:
                            if delivery_note_lines.note_id.currency_id.id != issue.product_id.manufacturer.property_product_pricelist_purchase.currency_id.id:
                                import_currency_rate=delivery_note_lines.note_id.currency_id.get_exchange_rate(issue.product_id.manufacturer.property_product_pricelist_purchase.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                            else:
                                import_currency_rate = 1
                        else:
                            if delivery_note_lines.note_id.currency_id.id !=issue.analytic_account_id.company_id.currency_id.id:
                                import_currency_rate=delivery_note_lines.note_id.currency_id.get_exchange_rate(issue.analytic_account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                            else:
                                import_currency_rate = 1
                    if delivery_note_lines.note_id.delivery_note_origin.name:
                        origin=delivery_note_lines.note_id.delivery_note_origin.name
                    else:
                        origin=delivery_note_lines.note_id.name
                        #Add line to invoice, included the line of delivery note
                        invoice_line={
                                    'product_id':delivery_note_lines.product_id.id,
                                    'name': issue.product_id.description +'-'+delivery_note_lines.name,
                                    'quantity':delivery_note_lines.quantity,
                                    'real_quantity':delivery_note_lines.quantity,
                                    'uos_id':delivery_note_lines.product_uos.id,
                                    'price_unit':delivery_note_lines.price_unit*import_currency_rate,
                                    'discount':delivery_note_lines.discount,
                                    'invoice_line_tax_id':[(6, 0, [tax.id for tax in delivery_note_lines.taxes_id])],
                                    'account_analytic_id':issue.analytic_account_id.id,
                                    'reference':'NE#'+ origin,
                                    'account_id':delivery_note_lines.product_id.property_account_income.id or delivery_note_lines.product_id.categ_id.property_account_income_categ.id
                                    }
                        #If Warranty is seller, the line invoices to customer included prices in zero
                        if issue.warranty=='seller':
                            invoice_line['price_unit']=0
                        #If lines detail, the invoice of products should be different to invoice services
                        if line_detailed==True:
                            if first_line_product==0:
                                inv_prod=invoice_obj.create(invoice_dict)
                                if issue.issue_number not in inv_prod.origin:
                                    inv_prod.write({'origin':inv_prod.origin + issue.issue_number +'-'})
                                invoices_list.append(inv_prod.id)
                                first_line_product+=1
                            #Condition for determine if the invoice doesn't exceed the limit of lines of products, if is exceed a new invoice should be generated
                            if count_lines_products<=limit_lines or limit_lines==0 or limit_lines==-1:
                                if issue.issue_number not in inv_prod.origin:
                                    inv_prod.write({'origin':inv_prod.origin + issue.issue_number +'-'})
                                inv_prod.write({'invoice_line':[(0,0,invoice_line)]})
                                inv_prod.write({'issue_ids':[(4,issue.id)]})
                                backorder.delivery_note_id.write({'invoice_ids':[(4,inv_prod.id)]})
                                count_lines_products+=1
                            else:
                                if issue.issue_number not in inv_prod.origin:
                                    inv_prod.write({'origin':inv_prod.origin + issue.issue_number})
                                inv_prod=invoice_obj.create(invoice_dict)
                                invoices_list.append(inv_prod.id)
                                count_lines_products=0
                                if issue.issue_number not in inv_prod.origin:
                                    inv_prod.write({'origin':inv_prod.origin + issue.issue_number +'-'})
                                inv_prod.write({'invoice_line':[(0,0,invoice_line)]})
                                inv_prod.write({'issue_ids':[(4,issue.id)]})
                                backorder.delivery_note_id.write({'invoice_ids':[(4,inv_prod.id)]})
                                count_lines_products+=1
                        else:
                            inv_prod=False
                            #Condition for determine if the invoice doesn't exceed the limit of lines, if is exceed a new invoice should be generated
                            if count_lines<=limit_lines or limit_lines==0 or limit_lines==-1:
                                if issue.issue_number not in inv.origin:
                                    inv.write({'origin':inv.origin + issue.issue_number +'-'})
                                inv.write({'invoice_line':[(0,0,invoice_line)]})
                                inv.write({'issue_ids':[(4,issue.id)]})
                                backorder.delivery_note_id.write({'invoice_ids':[(4,inv.id)]})
                                count_lines+=1
                            else:
                                if issue.issue_number not in inv.origin:
                                    inv.write({'origin':inv.origin + issue.issue_number})
                                inv=invoice_obj.create(invoice_dict)
                                invoices_list.append(inv.id)
                                count_lines=1
                                if issue.issue_number not in inv.origin:
                                    inv.write({'origin':inv.origin + issue.issue_number +'-'})
                                inv.write({'invoice_line':[(0,0,invoice_line)]})
                                inv.write({'issue_ids':[(4,issue.id)]})
                                backorder.delivery_note_id.write({'invoice_ids':[(4,inv.id)]})
                                count_lines+=1
                        backorder.write({'invoice_state':'invoiced'})
                        backorder.move_lines.write({'invoice_state':'invoiced'})
                        backorder.delivery_note_id.write({'state':'invoiced'})
        return count_lines,inv or False,count_lines_products,invoices_list,first_line_product,count_lines_products,inv_prod
    @api.multi
    def create_invoice_lines_timesheets(self,issue,count_lines,limit_lines,is_warranty,inv,invoice_dict,invoices_list):
        #Method for invoice each timesheet line included in issue
        #Exchange currency rates, based in parter settings of invoice
        account_obj=self.env['account.analytic.account']
        invoice_obj=self.env['account.invoice']
        for timesheet in issue.timesheet_ids:
            for account_line in timesheet.line_id:
                if not account_line.invoice_id:
                    total_timesheet=0.0
                    # Get quantity and price of timesheet based in rate prices of analytic account
                    quantity,total_timesheet=account_obj._get_invoice_price(account_line.account_id,account_line.date,timesheet.start_time,timesheet.end_time,issue.product_id.id,issue.categ_id.id,account_line.unit_amount,timesheet.service_type,timesheet.employee_id.id,account_line.to_invoice.id)
                    #If not is warranty, the invoice lines use the customer partner settings
                    if is_warranty==False:
                        if issue.partner_id and issue.branch_id:
                            if issue.branch_id.property_product_pricelist:
                                if account_line.account_id.pricelist_id.currency_id.id != issue.branch_id.property_product_pricelist.currency_id.id:
                                    import_currency_rate=account_line.account_id.pricelist_id.currency_id.get_exchange_rate(issue.branch_id.property_product_pricelist.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                                else:
                                    import_currency_rate = 1
                            else:
                                if account_line.account_id.pricelist_id.currency_id.id != account_line.account_id.company_id.currency_id.id:
                                    import_currency_rate=account_line.account_id.pricelist_id.currency_id.get_exchange_rate(account_line.account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                                else:
                                    import_currency_rate = 1
                        elif issue.partner_id and not issue.branch_id:
                            if issue.partner_id.property_product_pricelist:
                                if account_line.account_id.pricelist_id.currency_id.id != issue.partner_id.property_product_pricelist.currency_id.id:
                                    import_currency_rate=account_line.account_id.pricelist_id.currency_id.get_exchange_rate(issue.partner_id.property_product_pricelist.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                                else:
                                    import_currency_rate = 1
                            else:
                                if account_line.account_id.pricelist_id.currency_id.id != account_line.account_id.company_id.currency_id.id:
                                    import_currency_rate=account_line.account_id.pricelist_id.currency_id.get_exchange_rate(account_line.account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                                else:
                                    import_currency_rate = 1
                    #If Warranty is seller, the line invoices to customer included prices in zero
                    elif is_warranty==True:
                        if issue.product_id.manufacturer.property_product_pricelist_purchase:
                            if account_line.account_id.pricelist_id.currency_id.id != issue.product_id.manufacturer.property_product_pricelist_purchase.currency_id.id:
                                import_currency_rate=account_line.account_id.pricelist_id.currency_id.get_exchange_rate(issue.product_id.manufacturer.property_product_pricelist_purchase.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                            else:
                                import_currency_rate = 1
                        else:
                            if account_line.account_id.pricelist_id.currency_id.id != account_line.account_id.company_id.currency_id.id:
                                import_currency_rate=account_line.account_id.pricelist_id.currency_id.get_exchange_rate(account_line.account_id.company_id.currency_id,date.strftime(date.today(), "%Y-%m-%d"))[0]
                            else:
                                import_currency_rate = 1
                    if (timesheet.end_time-timesheet.start_time!=0 or total_timesheet!=0):
                        #Add line to invoice, included the line of timesheet
                        invoice_line={
                                      'product_id':account_line.product_id.id ,
                                      'name': account_line.product_id.description+'-'+issue.product_id.description,
                                      'real_quantity':timesheet.end_time-timesheet.start_time,
                                      'quantity':quantity,
                                      'price_unit':total_timesheet*import_currency_rate,
                                      'uos_id':account_line.product_id.uom_id.id,
                                      'discount':account_line.account_id.to_invoice.factor,
                                      'account_analytic_id':account_line.account_id.id,
                                      'price_subtotal':total_timesheet*quantity*import_currency_rate,
                                      'invoice_line_tax_id':[(6, 0, [tax.id for tax in account_line.product_id.taxes_id])],
                                      'account_id':account_line.product_id.property_account_income.id or account_line.product_id.categ_id.property_account_income_categ.id
                                        }
                        if timesheet.ticket_number:
                            invoice_line['reference']='R#'+timesheet.ticket_number
                        #If Warranty is seller, the line invoices to customer included prices in zero
                        if issue.warranty=='seller':
                            invoice_line['price_unit']=0
                        #Condition for determine if the invoice doesn't exceed the limit of lines, if is exceed a new invoice should be generated
                        if count_lines<=limit_lines or limit_lines==0 or limit_lines==-1:
                            inv.write({'invoice_line':[(0,0,invoice_line)]})
                            if issue.issue_number not in inv.origin:
                                inv.write({'origin':inv.origin + issue.issue_number +'-'})
                            inv.write({'issue_ids':[(4,issue.id)]})
                            count_lines+=1
                        else:
                            if issue.issue_number not in inv.origin:
                                inv.write({'origin':inv.origin + issue.issue_number})
                            inv=invoice_obj.create(invoice_dict)
                            invoices_list.append(inv.id)
                            count_lines=1
                            inv.write({'invoice_line':[(0,0,invoice_line)]})
                            if issue.issue_number not in inv.origin:
                                inv.write({'origin':inv.origin + issue.issue_number +'-'})
                            inv.write({'issue_ids':[(4,issue.id)]})
                            count_lines+=1
                    account_line.write({'invoice_id':inv.id})
        return count_lines,inv or False,invoices_list
    @api.multi
    def create_invoice_lines_issues(self,issues,invoice_dict,line_detailed,is_warranty):
        invoice_obj=self.env['account.invoice']
        user = self.env['res.users'].browse(self._uid)
        total_expenses=0.0
        count_lines=1
        product_expense=False
        count_lines_products=1
        first_line_product=0
        invoices_list=[]
        cont_invoice=0
        inv_prod=False
        #Define maximun number lines by invoice
        limit_lines=user.company_id.maximum_invoice_lines
        if line_detailed==True:
            for issue in issues:
                if issue.timesheet_ids or issue.expense_line_ids and cont_invoice==0:
                    cont_invoice=1
                    break
        #Define the initial invoice
        if cont_invoice==1 or line_detailed==False:
            inv=invoice_obj.create(invoice_dict)
            invoices_list.append(inv.id)
        #For each issue realized the invoices of a items (timesheets, backorders,supllier invoices lines, expenses lines, additional costs). Return the list of invoices generated
        for issue in issues:
            count_lines,inv,invoices_list=self.create_invoice_lines_timesheets(issue,count_lines,limit_lines,is_warranty,inv,invoice_dict,invoices_list)
            count_lines,inv,count_lines_products,invoices_list,first_line_product,count_lines_products,inv_prod=self.create_invoice_lines_backorders(issue,count_lines,limit_lines,line_detailed,first_line_product,count_lines_products,is_warranty,inv,invoice_dict,invoices_list,inv_prod)
            count_lines,inv,count_lines_products,invoices_list,first_line_product,count_lines_products,inv_prod=self.create_invoice_lines_supplier_invoices(issue,is_warranty,line_detailed,first_line_product,invoice_dict,invoices_list,count_lines_products,limit_lines,count_lines,inv,inv_prod)
            count_lines,inv,invoices_list=self.create_invoice_lines_additional_costs(issue,count_lines,limit_lines,is_warranty,inv,invoice_dict,invoices_list)
            count_lines,inv,invoices_list=self.create_invoice_lines_expenses(issue,is_warranty,total_expenses,product_expense,count_lines,limit_lines,invoice_dict,invoices_list,inv)
        return invoices_list
    @api.multi
    def get_date_due(self,partner):
        account_payment_term_obj = self.env['account.payment.term']
        date_due = False
        if partner.property_payment_term:
            pterm_list= account_payment_term_obj.compute(partner.property_payment_term.id, value=1,date_ref=time.strftime('%Y-%m-%d'))
            if pterm_list:
                pterm_list = [line[0] for line in pterm_list]
                pterm_list.sort()
                date_due = pterm_list[-1]
        return date_due
    @api.multi
    def generate_invoices_issues(self,issues_ids,group,line_detailed):
        #Define the structure of invoices generated with the issues invoices wizard, based in parameters selected
        issue_obj=self.env['project.issue']
        partner_obj=self.env['res.partner']
        user = self.env['res.users'].browse(self._uid)
        invoices_list=[]
        branch_issue_ids=[]
        partner_issue_ids=[]
        partner_group_ids=[]
        branch_group_ids=[]
        if group==False:
            for issue in issues_ids:
                invoice={
                    'date_invoice':datetime.strftime(datetime.today(), "%Y-%m-%d"),
                    'company_id':issue.analytic_account_id.company_id.id,
                    'fiscal_position':issue.product_id.manufacturer.property_account_position.id,
                    'origin':_('Issue #')
                    }
                ctx = dict(self._context)
                ctx['force_company']=issue.analytic_account_id.company_id.id
                ctx['company_id']=issue.analytic_account_id.company_id.id
                if issue.branch_id and issue.partner_id:
                    invoice['partner_id']=issue.branch_id.id
                    invoice['account_id']=issue.branch_id.property_account_receivable.id
                    invoice['currency_id']=issue.branch_id.property_product_pricelist.currency_id.id or issue.analytic_account_id.company_id.currency_id.id
                    invoice['payment_term']=issue.branch_id.property_payment_term.id
                    invoice['date_due']=self.get_date_due(issue.branch_id)
                    ctx['lang']=issue.branch_id.lang
                elif not issue.branch_id and issue.partner_id:
                    invoice['partner_id']=issue.partner_id.id
                    invoice['account_id']=issue.partner_id.property_account_receivable.id
                    invoice['currency_id']=issue.partner_id.property_product_pricelist.currency_id.id or issue.analytic_account_id.company_id.currency_id.id
                    invoice['payment_term']=issue.partner_id.property_payment_term.id
                    invoice['date_due']=self.get_date_due(issue.partner_id)
                    ctx['lang']=issue.partner_id.lang
                self = self.with_context(ctx)
                invoices_list+=self.create_invoice_lines_issues(issue,invoice,line_detailed,is_warranty=False)
        elif group==True:
            for issue in issues_ids:
                if issue.partner_id and issue.branch_id:
                    branch_issue_ids.append(issue.id)
                    if issue.branch_id.id not in branch_group_ids:
                        branch_group_ids.append(issue.branch_id.id)
                elif issue.partner_id and not issue.branch_id:
                    partner_issue_ids.append(issue.id)
                    if issue.partner_id.id not in partner_group_ids:
                        partner_group_ids.append(issue.partner_id.id)
            for partner in partner_group_ids:
                partner_id=partner_obj.browse(partner)
                issue_partner_ids=issue_obj.search([('id','in',partner_issue_ids),('partner_id','=',partner),('branch_id','=',False)],order='categ_id asc,product_id asc,create_date asc')
                invoice={
                        'date_invoice':datetime.strftime(datetime.today(), "%Y-%m-%d"),
                        'company_id':user.company_id.id,
                        'currency_id':partner_id.property_product_pricelist.currency_id.id or user.company_id.currency_id.id,
                        'fiscal_position':partner_id.property_account_position.id,
                        'origin':_('Issue #'),
                        'partner_id':partner_id.id,
                        'account_id':partner_id.property_account_receivable.id,
                        'payment_term':partner_id.property_payment_term.id,
                        'date_due':self.get_date_due(partner_id)
                        }
                ctx = dict(self._context)
                ctx['force_company']=user.company_id.id
                ctx['company_id']=user.company_id.id
                ctx['lang']=partner_id.lang
                self = self.with_context(ctx)
                invoices_list+=self.create_invoice_lines_issues(issue_partner_ids,invoice,line_detailed,is_warranty=False)
            for branch in branch_group_ids:
                branch_id=partner_obj.browse(branch)
                issue_branch_ids=issue_obj.search([('id','in',branch_issue_ids),('branch_id','=',branch),('partner_id','!=',False)],order='categ_id asc,product_id asc,create_date asc')
                invoice={
                        'date_invoice':datetime.strftime(datetime.today(), "%Y-%m-%d"),
                        'company_id':user.company_id.id,
                        'currency_id':branch_id.property_product_pricelist.currency_id.id or user.company_id.currency_id.id,
                        'fiscal_position':branch_id.property_account_position.id,
                        'origin':_('Issue #'),
                        'partner_id':branch_id.id,
                        'account_id':branch_id.property_account_receivable.id,
                        'payment_term':branch_id.property_payment_term.id,
                        'date_due':self.get_date_due(branch_id)
                        }
                ctx = dict(self._context)
                ctx['force_company']=user.company_id.id
                ctx['company_id']=user.company_id.id
                ctx['lang']=branch_id.lang
                self = self.with_context(ctx)
                invoices_list+=self.create_invoice_lines_issues(issue_branch_ids,invoice,line_detailed,is_warranty=False)
        return invoices_list
    @api.multi
    def generate_invoices_warranty_manufacturer(self,issues_ids,line_detailed):
        #Define the structure of warrant invoices generated with the issues invoices wizard, based in parameters selected
        journal_obj=self.env['account.journal']
        invoices_list=[]
        for issue in issues_ids:
            journal_id=journal_obj.search([('warranty_manufacturer', '=', True)])
            if not journal_id:
                raise Warning(_('Must configure a journal for warranty manufacturer'))
            invoice={
                    'journal_id':journal_id.id,
                    'partner_id':issue.product_id.manufacturer.id,
                    'account_id':issue.product_id.manufacturer.property_account_receivable.id,
                    'payment_term':issue.product_id.manufacturer.property_payment_term.id,
                    'date_invoice':datetime.strftime(datetime.today(), "%Y-%m-%d"),
                    'name':_('(Warranty Manufacturer)'),
                    'company_id':issue.analytic_account_id.company_id.id,
                    'currency_id':issue.product_id.manufacturer.property_product_pricelist_purchase.currency_id.id or issue.analytic_account_id.company_id.currency_id.id,
                    'fiscal_position':issue.product_id.manufacturer.property_account_position.id,
                    'date_due':self.get_date_due(issue.product_id.manufacturer),
                    'origin':_('Issue #')
                    }
            ctx = dict(self._context)
            ctx['lang']=issue.product_id.manufacturer.lang
            ctx['force_company']=issue.analytic_account_id.company_id.id
            ctx['company_id']=issue.analytic_account_id.company_id.id
            self = self.with_context(ctx)
            invoices_list=self.create_invoice_lines_issues(issue,invoice,line_detailed,is_warranty=True)
        return invoices_list
    @api.multi
    def generate_invoices(self,issue_ids,issue_list,group,line_detailed):
        issue_obj=self.env['project.issue']
        invoice_obj=self.env['account.invoice']
        invoices_list=[]
        #Issues Warranty Manufaturer
        issues_warranty_manufacturer=issue_obj.search([('warranty','=','manufacturer'),('id','in',issue_list)],order='categ_id asc,product_id asc,create_date asc')
        if issues_warranty_manufacturer:
            invoices_list+=self.generate_invoices_warranty_manufacturer(issues_warranty_manufacturer,line_detailed)
        #Normal Issues
        issues_default=issue_obj.search(['|',('warranty','=',False),('warranty','!=','manufacturer'),('id','in',issue_list)],order='categ_id asc,product_id asc,create_date asc')
        if issues_default:
            invoices_list+=self.generate_invoices_issues(issues_default,group,line_detailed)
        
        for invoice in invoice_obj.browse(invoices_list):
            if invoice.origin[-1:]=='-':
                invoice.write({'origin':invoice.origin[:-1]})
        return invoices_list

    @api.multi
    def validate_issues(self):
        #Define filter of issues to invoice based in parameters wizard
        account_analytic_list=[]
        partner_ids=[]
        issue_ids=[]
        issue_obj=self.env['project.issue']
        for account in self.env['account.analytic.account'].search(['|',('invoice_on_timesheets','=',True),('charge_expenses','=',True)]):
            account_analytic_list.append(account.id)
        if self.filter=='filter_no':
            issue_ids=issue_obj.search(['|','|','|',('additional_cost_ids','!=',False),('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('analytic_account_id','!=',False),('analytic_account_id','in',account_analytic_list),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_ids','=',False)],order='categ_id asc,product_id asc,create_date asc')
        elif self.filter=='filter_date':
            issue_ids=issue_obj.search(['|','|','|',('additional_cost_ids','!=',False),('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('analytic_account_id','!=',False),('analytic_account_id','in',account_analytic_list),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_ids','=',False),('create_date', '>=', self.date_from),('create_date', '<=', self.date_to)],order='categ_id asc,product_id asc,create_date asc')
        elif self.filter=='filter_period':
            issue_ids=issue_obj.search(['|','|','|',('additional_cost_ids','!=',False),('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('analytic_account_id','!=',False),('analytic_account_id','in',account_analytic_list),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_ids','=',False),('create_date', '>=',self.period_from.date_start),('create_date', '<=',self.period_to.date_stop)],order='categ_id asc,product_id asc,create_date asc')
        elif self.filter=='filter_partner':
            for partner in self.partner_ids:
                partner_ids.append(partner.id)
            issue_ids=issue_obj.search(['&','|','|','|',('additional_cost_ids','!=',False),('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),'|',('partner_id','in',partner_ids),('branch_id','in',partner_ids),('issue_type','!=','preventive check'),('analytic_account_id','!=',False),('analytic_account_id','in',account_analytic_list),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_ids','=',False)],order='categ_id asc,product_id asc,create_date asc')
        elif self.filter=='filter_issue':
            for issue in self.issue_ids:
                issue_ids.append(issue.id)
            issue_ids=issue_obj.search(['|','|','|',('additional_cost_ids','!=',False),('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('analytic_account_id','!=',False),('analytic_account_id','in',account_analytic_list),('analytic_account_id.charge_expenses','=',True),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_ids','=',False),('id','in',issue_ids)],order='categ_id asc,product_id asc,create_date asc')
        self.issue_invoice_ids=issue_ids
        if self.filter:
            self.write({'state':'done'})
        return {
            'name': _('Issues to Invoice'),
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            }

    @api.multi
    def invoice_issues(self):
        issue_list=[]
        invoices_list=[]
        if self.issue_invoice_ids:
            for issue in self.issue_invoice_ids:
                issue_list.append(issue.id)
            invoices_list=self.generate_invoices(self.issue_invoice_ids,issue_list,self.group_customer,self.line_detailed)
        result = self.env['ir.model.data'].get_object_reference('account', 'action_invoice_tree1')
        id = result and result[1] or False
        act_win = self.env['ir.actions.act_window'].search_read([('id','=',id)])[0]
        act_win['domain']=[('id','in',invoices_list),('type','=','out_invoice')]
        act_win['name'] = _('Invoices')
        return act_win
    @api.one
    @api.constrains('date_from','date_to')
    def _check_filter_date(self):
        if self.filter=='filter_date':
            if self.date_from>self.date_to:
                raise Warning(_('Start Date must be less than End Date'))
    @api.constrains('period_from','period_to')
    def _check_filter_period(self):
        if self.filter=='filter_period':
            if self.period_from.date_start>self.period_to.date_stop:
                raise Warning(_('Start Period must be less than End Period'))
    @api.onchange('filter')
    def get_account_issues(self):
        if self.filter=='filter_issue':
            account_analytic_list=[]
            for account in self.env['account.analytic.account'].search(['|',('invoice_on_timesheets','=',True),('charge_expenses','=',True)]):
                account_analytic_list.append(account.id)
            self.init_onchange_call=self.env['project.issue'].search(['|','|','|',('additional_cost_ids','!=',False),('backorder_ids','!=',False),('expense_line_ids','!=',False),('timesheet_ids','!=',False),('issue_type','!=','preventive check'),('stage_id.closed','=',True),('sale_order_id','=',False),('invoice_ids','=',False),('analytic_account_id','in',account_analytic_list)])
        else:
            self.issue_ids=False
    line_detailed=fields.Boolean(string="Product lines separate service lines",default=True)
    group_customer=fields.Boolean( string="Group by customer",default=True)
    filter=fields.Selection([('filter_no','No Filter'),('filter_date','Date'),('filter_period','Period'),('filter_partner','Partner'),('filter_issue','Issue')],string="Filter",required=True,default='filter_no')
    date_from=fields.Date(string="Start Date")
    date_to=fields.Date(string="End Date")
    fiscalyear_id=fields.Many2one('account.fiscalyear',string="Fiscal Year")
    init_onchange_call= fields.Many2many('project.issue',compute="get_account_issues",string='Nothing Display', help='field at view init')
    period_to= fields.Many2one('account.period',string="End Period")
    period_from= fields.Many2one('account.period',string="Start Period")
    partner_ids= fields.Many2many('res.partner',string="Customers")
    issue_ids=fields.Many2many('project.issue','project_issue_project_issue_wizard_rel',string="Issues")
    issue_invoice_ids=fields.One2many('project.issue',compute='validate_issues',string="Issues")
    state= fields.Selection([('validate','Validate'),('done','Done')], string='State')
    
    _defaults = {
        'state': 'validate'
    }