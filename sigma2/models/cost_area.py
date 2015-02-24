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

class sigma2_cost_area(models.Model):
    """Áreas de coste para mantenimiento"""

    _name = 'sigma2.cost.area'
    _description = 'Maintenance Cost Area'

    code = fields.Char('Código', required=True, select=True)
    name = fields.Char('Nombre', required=True, select=True)
    investment = fields.Boolean('Inversion')
    notes = fields.Text('Notas')
    active = fields.Boolean('Registro activo')
    parent_id = fields.Many2one('sigma2.cost.area', 'Área de coste padre', select=True, ondelete='restrict')
    child_id = fields.One2many('sigma2.cost.area', 'parent_id', string='Áreas de coste hijas')

    _defaults = {
        'active': True,
    }

    _order = 'code'

    _sql_constraints = [
        ('code_uniq', 'unique(code)', _("No pueden existir dos áreas de coste con el mismo código!")),
        ('name_uniq', 'unique(name)', _("No pueden existir dos áreas de coste con el mismo nombre!"))
    ]

    @api.one
    @api.constrains('parent_id')
    def _check_parent(self):
        if self.parent_id and \
            self.parent_id.code == self.code :
                raise Warning(_('Error! No se pueden crear áreas de coste recursivas.'))

