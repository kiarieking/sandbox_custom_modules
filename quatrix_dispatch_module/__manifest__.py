# -*- coding: utf-8 -*-
{
    'name': "Quatrix Dispatch",

    'summary': """Dispatch Module for Quatrix Operations""",

    'description': """
        This module/app will be used to dispatch any trips by the quatrix dispatch/operations team.
    """,

    'author': "Murunga Kibaara, Wilson Ndirangu",
    'website': "https://www.quatrixglobal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Logistics',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'product', 'purchase', 'account', 'fleet', 'quatrix_inheritance_module'],
    'external_dependencies': {
        'python': ['python-dotenv', 'cloudinary', 'phonenumbers']
    },

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/purchase_sequence.xml',
        'data/lpo_sequence.xml',
        'views/dispatch_views.xml',
        'views/purchase_views.xml',
        'views/purchase_dispatch.xml',
        'views/report_views.xml',
        'wizards/general_reports_wizard.xml',
        'wizards/dispatch_report_wizard.xml',
        'wizards/carrier_reports_wizard.xml',
        'reports/report_dispatch.xml',
        'reports/quatrix_dispatch_reports.xml',
        'reports/dispatch_report.xml',
        'reports/quatrix_carrier_report.xml',
        'wizards/customer_revenue_cost_wizard.xml',
        'reports/customer_revenue_cost_report.xml',
        'wizards/tonnage_revenue_report.xml',
        'reports/tonnage_revenue_cost.xml',
        'reports/report.xml'
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
