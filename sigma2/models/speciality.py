# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import SUPERUSER_ID
from openerp import models, fields, api, _

from datetime import date
import logging

_logger = logging.getLogger(__name__)

class sigma2_speciality(models.Model):
    """Especialidades de mantenimiento"""

    _name = 'sigma2.speciality'
    _description = 'Maintenance Speciality'

    name = fields.Char('Nombre', required=True, select=True)
    notes = fields.Text('Notas')
    active = fields.Boolean('Registro activo')

    _defaults = {
        'active': True,
    }

    _order = 'name'

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _("No pueden existir dos especialidades con el mismo nombre!"))
    ]
