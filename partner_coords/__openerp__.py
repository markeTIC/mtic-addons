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
    'name': 'Coordenadas en partners',
    'version': '1.0.04',
    'category': '',
    'sequence': 1,
    'complexity': 'easy',
    'license': 'AGPL-3',
    'author': 'markeTIC Solutions',
    'website': 'www.marketic.eu',
    'depends': ['base'],
    'summary': 'Coordenadas en partners',
    'description': """
Coordenadas en partners
=====================
Añade los campos de coordenadas en partners.
    """,
    'data': [
        'views/res_partner_view.xml',
    ],
    'demo': [],
    'test': [],
    'qweb': [],
    'application': False,
    'installable': True,
    'auto_install': False,
}
