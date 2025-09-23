# -*- coding: utf-8 -*-
{
    'name': "Fuel Management",

    'summary': """Module to allow users to record fuel vouchers.""",

    'description': """Module to allow users to record fuel vouchers.""",

    'author': "Murunga Kibaara",
    'website': "http://www.quatrixglobal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Logistics',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'fleet'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'reports/report.xml',
        'reports/fuel_voucher.xml',
        'data/sequence.xml',
        'wizard/report_wizard.xml',
        'wizard/report.xml',
        'wizard/partner_fuel_template.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
