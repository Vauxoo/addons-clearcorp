# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Client Pay Day',
    'summary': 'Add a pay day to client',
    'version': '8.0.1.0',
    'category': 'Accounting & Finance',
    'website': 'http://clearcorp.cr',
    'author': 'ClearCorp',
    'license': 'AGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,

    'depends': [
        'base',
        'account',
    ],
    'data': [
        'views/client_pay_day_view.xml',
        'views/invoice_pay_day_view.xml',
    ],


}
