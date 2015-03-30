# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2015 markeTIC Solutions (http://www.marketic.eu)
#                       Jose F. Fernandez <jffernandez@marketic.eu>
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
    'version': '1.0.40',
    'category': 'Mantenimiento',
    'sequence': 1,
    'complexity': 'easy',
    'license': 'AGPL-3',
    'author': 'markeTIC Solutions',
    'website': 'www.marketic.eu',
    'depends': ['note', 'purchase', 'manufacturer', 'hr', ],
    'summary': 'Sistema Integral de Gestión de Mantenimiento',
    'description': """
SIGMa 2  -  Sistema Integral de Gestión de Mantenimiento
=========================================================
Aplicación de gestión de mantenimiento preventivo, correctivo y gestión del almacén de recambios.

TODO:
    - crear grupos de permisos para mantenimiento:
        - usuario
        - manager
    - visualizacion de código de producto en tree
    
    """,
    'data': [
        'security/sigma2_security.xml',
        'security/ir.model.access.csv',
        'data/sequences.xml',
        'data/order_type.xml',
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
        'data/menu.xml',
    ],
    'demo': [],
    'test': [],
    'qweb': [],
    'application': True,
    'installable': True,
    'auto_install': False,
}
