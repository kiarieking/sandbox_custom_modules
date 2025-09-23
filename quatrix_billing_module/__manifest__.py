# -*- coding: utf-8 -*-
{
    'name': "Quatrix Billing",

    'summary': """
        Carrier billing module for Quatrix Global""",

    'description': """
        This module will be used to record all vendor expenses which can then be posted to account invoice
    """,

    'author': "Murunga Kibaara",
    'website': "https://www.quatrixglobal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounts & Finance',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/billing_view.xml',
        'reports/report.xml',
        'reports/billing_report.xml',
        'wizards/wizard.xml',
        'wizards/report.xml',
        'wizards/billing_ledger_template.xml'
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
