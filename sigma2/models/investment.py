# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import SUPERUSER_ID
from openerp import models, fields, api, _
from openerp.addons.decimal_precision import decimal_precision as dp

from datetime import date
import logging

_logger = logging.getLogger(__name__)

class sigma2_investment(models.Model):
    """Inversiones para mantenimiento"""

    _name = 'sigma2.investment'
    _description = 'Maintenance Investments'

    code = fields.Char('Código', required=True, select=True)
    year = fields.Integer('Ejercicio', required=True, select=True)
    name = fields.Char('Nombre', required=True, select=True)
    ammount = fields.Float('Importe', digits_compute= dp.get_precision('Account'))
    notes = fields.Text('Notas')
    active = fields.Boolean('Registro activo')

    _defaults = {
        'active': True,
    }

    _order = 'year, code'

    _sql_constraints = [
        ('code_uniq', 'unique(code)', _("No pueden existir dos inversiones con el mismo código!"))
    ]

