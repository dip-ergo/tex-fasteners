
# -*- coding: utf-8 -*-
###############################################################################
#
#    jeffery CHEN fan<jeffery9@gmail.com>
#
#    Copyright (c) All rights reserved:
#        (c) 2017  TM_FULLNAME
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses
#    
#    Odoo and OpenERP is trademark of Odoo S.A.
#
###############################################################################
{
    'name': 'Workorder Attendance',
    'summary': 'Human readable name Module Project',
    'version': '1.0',

    'description': """
==============================================


    """,

    'author': 'Ergo Ventures Pvt. Ltd.',
    'maintainer': 'Ergo Ventures Pvt. Ltd.',
    'contributors': ['Ergo Ventures Pvt. Ltd. <TM_FULLNAME@gmail.com>'],

    'website': 'https://www.ergo-ventures.com',

    'license': 'AGPL-3',
    'category': 'Uncategorized',

    'depends': [
        'mrp_workorder', 'hr_attendance'
    ],

    'data': [
        'security/ir.model.access.csv',
        'views/mrp_workorder_views.xml',
        'views/add_employee_view.xml',
        'views/hr_attendance_views.xml',
        'views/res_config.xml',
        'views/work_center.xml',
        'views/mrp_account.xml',
        'views/mrp_production.xml'
    ],
    'installable': True
}
