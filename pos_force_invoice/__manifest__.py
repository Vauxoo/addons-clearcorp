# -*- coding: utf-8 -*-
# © 2016 ClearCorp

{
    'name': 'PoS - Force invoice on ticket validation',
    'summary': 'This module forces the invoicing of every point of sale order.',
    'description': """
PoS - Force invoice on ticket validation
========================================

This module forces the invoicing of every point of sale order.

Credits
=======

Contributors
------------

* Carlos Vásquez <cv@cc.cr>

Maintainer
----------

This module is maintained by ClearCorp.
    """,
    'version': '1.0',
    'category': 'Point of Sale',
    'author': 'ClearCorp',
    'license': 'LGPL-3',
    'sequence': 10,
    'application': False,
    'installable': True,
    'auto_install': False,
    'depends': [
        'point_of_sale'
    ],
    'data': [
        'views/templates.xml',
    ],
}
