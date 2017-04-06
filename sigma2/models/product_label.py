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

class sigma2_product_label(models.Model):
    """Etiqueta de producto para mantenimiento"""

    _name = 'sigma2.product_label'
    _description = 'Maintenance Product Label'

    barcode = fields.Char('Código de barras', required=True, select=True)
    name = fields.Char('Nombre', required=True, select=True)
    code = fields.Char('Referencia')
    active = fields.Boolean('Registro activo')

    _defaults = {
        'active': True,
    }

    _order = 'code'

