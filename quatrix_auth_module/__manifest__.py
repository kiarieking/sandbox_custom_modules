# -*- coding: utf-8 -*-
{
    'name': "Quatrix Auth",

    'summary': """
        Quatrix Auth Module""",

    'description': """
        This module is used to allow users to authenticate HTTP requests using an api key
    """,

    'author': "Murunga Kibaara",
    'website': "https://www.quatrixglobal.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Security',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/auth_api_key.xml',
        'views/auth_api_key.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
