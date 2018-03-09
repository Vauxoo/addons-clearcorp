# -*- coding: utf-8 -*-
# © 2016 ClearCorp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Account Asset Track',
    'version': '1.0',
    'author': 'ClearCorp',
    'complexity': 'normal',
    'website': 'http://clearcorp.co.cr',
    'category': 'Accounting & Finance',
    'summary': 'Track Asset Lines Changes',
    'description': """
Asset Track Mail lines
==========================================
Track state changes in Assets.
    """,
    'depends': [
        'account_asset'
    ],
    'init_xml': [],
    'demo': [],
    'data': [
        'data/mail_message_subtypes.xml',
        'views/account_asset_track_view.xml',
    ],
    'license': 'AGPL-3',
    'installable': False,
    'active': False,
    'application': False,
}
