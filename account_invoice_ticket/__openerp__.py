# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Account Invoice Ticket',
    'summary': 'Print invoice in ticket format',
    'version': '9.0.1.0',
    'category': '',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'account',
    ],
    'data': [
        'data/account_invoice_ticket_data.xml',
        'views/account_invoice_ticket_report.xml',
        'views/report_account_invoice_ticket.xml'
    ]
}
