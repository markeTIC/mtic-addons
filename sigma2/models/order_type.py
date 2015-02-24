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

class sigma2_order_type(models.Model):
    """Tipos de orden de mantenimiento"""

    _name = 'sigma2.order.type'
    _description = 'Maintenance Order Type'

    code = fields.Char('Código', required=True)
    name = fields.Char('Nombre', required=True)
    counter = fields.Many2one('ir.sequence', 'Contador', ondelete='restrict')
    notes = fields.Text('Notas')
    active = fields.Boolean('Registro activo')

    _defaults = {
        'active': True,
    }

    _order = 'name'

    _sql_constraints = [
        ('code_uniq', 'unique(code)', _("No pueden existir dos tipos de orden con el mismo código!")),
        ('name_uniq', 'unique(name)', _("No pueden existir dos tipos de orden con el mismo nombre!"))
    ]
