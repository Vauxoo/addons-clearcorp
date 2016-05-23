# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Mail Private Message',
    'version': '8.0.1.2',
    'category': 'Mail',
    'sequence': 10,
    'summary': """Private messages and notifications""",
    'author': 'ClearCorp',
    'website': 'http://clearcorp.cr',
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
    'depends': ['mail', 'base'],
    'data': [
        'views/assets_backend.xml',
        'wizard/mail_compose_view.xml',
        'security/mail_private_message_security.xml',
    ],
    'qweb': ['static/src/xml/mail.xml'],
}
