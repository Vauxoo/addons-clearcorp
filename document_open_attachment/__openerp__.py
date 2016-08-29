# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Document Open Attachment',
    'version': '8.0.1.0',
    'category': '',
    'sequence': 10,
    'summary': """Edit attached details of attached files.""",
    'author': 'ClearCorp',
    'website': 'http://clearcorp.cr',
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'AGPL-3',
    'depends': ['document'],
    'data': ['views/assets_backend.xml'],
    'qweb': ['static/src/xml/document_open_attachment.xml']
}
