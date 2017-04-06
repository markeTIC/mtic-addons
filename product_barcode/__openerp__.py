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
    'name': 'Código de barras en productos',
    'version': '1.0.01',
    'category': '',
    'sequence': 1,
    'complexity': 'easy',
    'license': 'AGPL-3',
    'author': 'Fenix Engineering Solutions',
    'website': 'www.fenix-es.com',
    'depends': ['base', 'product'],
    'summary': 'Código de barras en productos',
    'description': """
Código de barras en productos
=============================
- Añade el campo barcode al producto.
- Elimina el campo ean13 del formulario.
    """,
    'data': [
        'views/product_inherit.xml',
    ],
    'demo': [],
    'test': [],
    'qweb': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
