# -*- coding: utf-8 -*-
{
    'name': "Quatrix Payments",

    'summary': """
        Customer/Vendor payments module for Quatrix Global""",

    'description': """
        This module tries to resolve the customer/supplier payments issue on odoo
    """,

    'author': "Murunga Kibaara",
    'website': "http://www.quatrixglobal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounts - Payments',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale', 'purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'reports/report.xml',
        'reports/supplier_report.xml',
        'wizards/supplier_report_wizard.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
