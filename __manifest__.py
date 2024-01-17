# -*- coding: utf-8 -*-
{
    'name': "sd_contacts",

    'summary': """
        """,

    'description': """
        
    """,

    'author': "Arash Homayounfar",
    'website': "https://gilaneh.com/",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Service Desk/Service Desk',
    'application': True,
    'version': '15.0.1.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'website', 'hr'],

    # always loaded
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        # 'views/data.xml',
        'views/employee_contacts.xml',
        ],
    'assets': {
        'web._assets_common_scripts': [
        ],
        'web._assets_common_styles': [
        ],
        'web.assets_qweb': [
            'sd_contacts/static/src/components/**/*.xml',
        ],
        'web.assets_backend': [
        ],
        'web.assets_frontend': [
            'sd_contacts/static/src/components/**/*.scss',
            'sd_contacts/static/src/components/**/*.js',
        ],
        'web.report_assets_common': [
        ],
        },
    'license': 'LGPL-3',
}
