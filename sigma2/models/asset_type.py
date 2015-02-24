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

class sigma2_asset_type(models.Model):
    """Tipos de activos para mantenimiento"""

    _name = 'sigma2.asset.type'
    _description = 'Maintenance Asset Type'

    name = fields.Char('Nombre', required=True, select=True)
    type = fields.Selection(
        selection=[
            ('line', 'Línea'),
            ('machine', 'Máquina'),
            ('subset', 'Subconjunto'),
            ('part', 'Pieza'),
            ('installation', 'Instalación'),
            ('tool', 'Herramienta'),
            ('appliance', 'Útil'),
            ('measuring_device', 'Equipo de medida'),
        ],
        required=True,
        string='Tipo interno')
    corrective = fields.Boolean('Correctivo')
    preventive = fields.Boolean('Preventivo')
    calibration = fields.Boolean('Calibración')
    notes = fields.Text('Notas')
    active = fields.Boolean('Registro activo')

    _defaults = {
        'active': True,
        'type': 'part',
        'corrective': False,
        'preventive': False,
        'calibration': False,
    }

    _order = 'name'

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _("No pueden existir dos tipos con el mismo nombre!"))
    ]
    
