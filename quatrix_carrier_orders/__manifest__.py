# -*- coding: utf-8 -*-
{
    'name': "Carrier Orders",

    'summary': """
        Create RFQ's for carriers.
        """,

    'description': """
        Process orders from dispatch and create RFQ's from carriers.
    """,

    'author': "Murunga Kibaara",
    'website': "http://www.quatrixglobal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Dispatch & Orders',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'product', 'fleet', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'currency': 'KES'
}
