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
    'version': '18.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'website', 'hr',],

    # always loaded
    'data': [
        # 'security/security.xml',
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/res_users.xml',
        'views/hr_employee.xml',
        'views/employee_contacts.xml',
        'views/settings.xml',
        ],
    'assets': {
        'web._assets_common_scripts': [
        ],
        'web._assets_common_styles': [
        ],
        'web.assets_qweb': [

        ],
        'web.assets_backend': [
            'sd_contacts/static/src/components/web/**/*.xml',
            'sd_contacts/static/src/components/web/**/*.scss',
            'sd_contacts/static/src/components/web/**/*.js',
        ],
        'web.assets_frontend': [
            'sd_contacts/static/src/components/website/**/*.js',
            'sd_contacts/static/src/components/website/**/*.scss',
            'sd_contacts/static/src/components/website/**/*.xml',
        ],
        'web.report_assets_common': [

        ],
        },
    'images': [
        'static/src/img/user_avatar_100.png',
    ],
    'license': 'LGPL-3',
}

