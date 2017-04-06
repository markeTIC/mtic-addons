# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2017 Fenix Engineering Solutions (http://www.fenix-es.com)
#                       Jose F. Fernandez <jffernandez@fenix-es.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'SIGMa 2',
    'version': '1.1.58',
    'category': 'Mantenimiento',
    'sequence': 1,
    'complexity': 'easy',
    'license': 'AGPL-3',
    'author': 'Fenix Engineering Solutions',
    'website': 'www.fenix-es.com',
    'depends': ['note', 'purchase', 'manufacturer', 'hr', 'web_dashboard_open_action', ],
    'summary': 'Sistema Integral de Gestión de Mantenimiento',
    'description': """
SIGMa 2  -  Sistema Integral de Gestión de Mantenimiento
=========================================================
Aplicación de gestión de mantenimiento preventivo, correctivo y gestión del almacén de recambios.

    """,
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'data/sequences.xml',
        'data/order_type.xml',
        'data/email_templates.xml',
        'views/product_inherit.xml',
        'views/partner_inherit.xml',
        'views/purchase_inherit.xml',
        'views/procurement_inherit.xml',
        'views/location.xml',
        'views/cost_area.xml',
        'views/investment.xml',
        'views/asset_class.xml',
        'views/asset_type.xml',
        'views/asset.xml',
        'views/procedure.xml',
        'views/order_type.xml',
        'views/speciality.xml',
        'views/action_planning.xml',
        'views/maintenance_order.xml',
        'views/product_label.xml',
        'data/action_planning_cron.xml',
        'wizard/preventive_list_view.xml',
        'wizard/create_product_labels_view.xml',
        'wizard/maintenance_order_list_view.xml',
        'views/report_preventive_list.xml',
        'views/report_purchaseorder.xml',
        'views/report_purchasequotation.xml',
        'views/report_maintenance_order_list.xml',
        'sigma2_report.xml',
        'report/maintenance_order_report_view.xml',
        'report/purchase_invoice_report_view.xml',
        'views/stock_inherit.xml',
        'data/menu.xml',
    ],
    'demo': [],
    'test': [],
    'qweb': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
