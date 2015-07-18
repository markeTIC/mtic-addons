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
    'name': 'Competition Website',
    'version': '1.0.01',
    'category': 'Competition',
    'sequence': 1,
    'complexity': 'easy',
    'license': 'AGPL-3',
    'author': 'markeTIC Solutions',
    'website': 'www.marketic.eu',
    'depends': ['competition'],
    'summary': 'Módulo web para la gestión de competiciones',
    'description': """
Módulo web para la gestión de competiciones
===========================================


    """,
    'data': [
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'views/competition_website.xml',
    ],
    'demo': [],
    'test': [],
    'qweb': ['static/src/xml/*.xml'],
    'application': True,
    'installable': True,
    'auto_install': False,
}
