
{
    "name" : "Products Search Extends",
    "version" : "1.0",
    "author" : "SIESA",
    "category" : "Generic Modules/Inventory Control",
    "depends" : ["base", "process","product","sale", "decimal_precision","stock"],
    'complexity': "easy",
    "website" : "http://www.siesacr.com",
    "description": """
    This module add to product
    currency_id,
    part_number,
    fob_currency_id,
    cost_fob,
    and improve the search logic.

    """,
    'update_xml': [
        'product_view.xml',
    ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
