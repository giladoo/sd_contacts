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
    'version': '18.0.2.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'website', 'hr', 'hr_attendance'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/gates.xml',
        'views/send_list.xml',
        'report/present_list.xml',
        'report/present_list_template.xml',
        'report/attendance_list.xml',
        'report/attendance_list_template.xml',
        'wizard/attendance_report.xml',
        'wizard/attendance_report_template.xml',
        'views/res_users.xml',
        'views/hr_employee.xml',
        'views/employee_contacts.xml',
        'views/attendance.xml',
        'views/hr_leave.xml',
        'views/settings.xml',
        'views/hr_work_location.xml',
        'views/visitors_views.xml',
        ],
    'assets': {
        'web._assets_common_scripts': [
        ],
        'web._assets_common_styles': [
        ],
        'web.assets_qweb': [

        ],
        'web.assets_backend': [
            'sd_contacts/static/src/components/web/**/*.*',
            'sd_contacts/static/src/components/security_gates/**/*.*',

        ],
        'web.assets_frontend': [
            'sd_contacts/static/src/components/website/**/*.*',

        ],
        'web.report_assets_pdf': [
            'sd_contacts/static/src/css/report_style.scss',
            # 'sd_contacts/static/src/components/security_gates/**/*.scss',

        ],
        },
    'images': [
        'static/src/img/user_avatar_100.png',
    ],
    'license': 'LGPL-3',
}







