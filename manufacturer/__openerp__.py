# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 - 2015 markeTIC Solutions (http://www.marketic.eu)
#                              Jose F. Fernandez <jffernandez@marketic.eu>
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
    'name': 'Fabricantes de productos',
    'version': '0.1.12',
    'category': 'Mantenimiento',
    'sequence': 1,
    'complexity': 'easy',
    'license': 'AGPL-3',
    'author': 'markeTIC Solutions',
    'website': 'www.marketic.eu',
    'depends': ['product'],
    'summary': 'Mantenimiento de fabricantes de productos',
    'description': """
Módulo de fabricantes
=====================
El módulo de fabricantes permite registrar los datos principales de los fabricantes de productos.
    """,
    'data': [
        'security/manufacturer_security.xml',
        'security/ir.model.access.csv',
        'data/manufacturer.xml',
        'views/manufacturer.xml',
        'views/product_template_manufacturer.xml',
    ],
    'demo': [],
    'test': [],
    'qweb': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
