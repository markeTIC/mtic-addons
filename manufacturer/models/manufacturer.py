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

class manufacturer_manufacturer(models.Model):
    """Fabricante de productos"""

    _name = 'manufacturer.manufacturer'
    _description = 'Manufacturer'
    _order = "name"

    name = fields.Char('Nombre', required=True, select=True)
    description = fields.Char('Descripción', select=True)
    website = fields.Char('Página web')
    logo = fields.Binary("Logo")
    partner_id = fields.Many2one('res.partner', 'Partner')
    notes = fields.Text('Notas')
    active = fields.Boolean('Registro activo')

    _defaults = {
        'active': True,
    }
