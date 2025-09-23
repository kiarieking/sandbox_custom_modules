# -*- coding: utf-8 -*-

{
    'name': "Total Solutions ETR Invoice Sign",

    'summary': """
        Kra electronically signs invoices.""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Eric Macharia",
    'website': "http://example.com",

    'category': 'Extra Tools',
    'version': '14.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['account', 'product', 'stock'],
    'external_dependencies': {'python': ['xmltodict']},
    'license': 'LGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'reports/invoice.xml',

        'views/res_models.xml',
        'views/account.xml',
        'views/stock.xml',
    ],
    'application': True
}
