{
    'name': 'Website Contact Form',
    'category': 'Website',
    'website': 'https://www.odoo.com/page/website-builder',
    'summary': 'Create Leads From Contact Form',
    'version': '1.0',
    'description': """
OpenERP Contact Form
====================

        """,
    'author': 'ClearCorp',
    'depends': ['website_partner', 'crm', 'website_crm'],
    'data': ['view.xml'],
    'css': [
            'static/src/css/style.css',
            ],
    'installable': True,
    'auto_install': False,
}
