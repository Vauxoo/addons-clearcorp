{
    'name': 'Purchase Import',
    'version': '1.1',
    'category': 'Purchases',
    'description': """
        Add a module that facilitates the purchase of imports, adding tax charges and
        change the price of the product cost for the total price movement.

    """,
    'author': 'SIESA',
    'website': 'http://www.siesacr.com',
    'depends': ['purchase','product','product_search_improver'],
    'data': [
        'import_view.xml',
        'voucher_view.xml',
        'purchase_import_workflow.xml',
        'product_view.xml',
        'tariff_view.xml',
        'import_sequence.xml'
    ],
    'installable': True,
    'active': False,
}
