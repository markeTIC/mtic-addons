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

class sigma2_location(models.Model):
    """Zona de fábrica para mantenimiento"""

    _name = 'sigma2.location'
    _description = 'Maintenance Location'

    name = fields.Char('Nombre', required=True, select=True)
    notes = fields.Text('Notas')
    active = fields.Boolean('Registro activo')
    parent_id = fields.Many2one('sigma2.location', 'Zona de fábrica padre', select=True, ondelete='restrict')
    child_id = fields.One2many('sigma2.location', 'parent_id', string='Zonas de fábrica hijas')

    _defaults = {
        'active': True,
    }

    _order = 'name'

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _("No pueden existir dos zonas de fábrica con el mismo nombre!"))
    ]

    @api.one
    @api.constrains('parent_id')
    def _check_parent(self):
        if self.parent_id and \
            self.parent_id.name == self.name :
                raise Warning(_('Error! No se pueden crear zonas de fábrica recursivas.'))
