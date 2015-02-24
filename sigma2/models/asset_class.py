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

class sigma2_asset_class(models.Model):
    """Clases de activos para mantenimiento"""

    _name = 'sigma2.asset.class'
    _description = 'Maintenance Asset Class'

    name = fields.Char('Nombre', required=True, select=True)
    regulatory_inspection = fields.Boolean('Inspección reglamentaria')
    applicable_regulations = fields.Char('Reglamento aplicable')
    notes = fields.Text('Notas')
    active = fields.Boolean('Registro activo')

    _defaults = {
        'active': True,
    }

    _order = 'name'

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _("No pueden existir dos clases con el mismo nombre!"))
    ]

    @api.onchange('regulatory_inspection')
    def regulatory_inspection_change(self):
        if not self.regulatory_inspection:
            if self.applicable_regulations:
                self.applicable_regulations = None
                