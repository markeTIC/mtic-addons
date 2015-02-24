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

class sigma2_procedure(models.Model):
    """Procedimiento de mantenimiento preventivo"""

    _name = 'sigma2.procedure'
    _description = 'Maintenance Procedure'

    code = fields.Char('Código', required=True, select=True)
    name = fields.Char('Nombre', required=True, select=True)
    display_name = fields.Char('Procedimiento', compute='_compute_display_name', search='_search_display_name',)
    notes = fields.Text('Notas')
    active = fields.Boolean('Registro activo')
    action_planning_ids = fields.One2many('sigma2.action.planning', 'procedure_id', string='Gamas del procedimiento')

    _rec_name = 'display_name'
    
    _defaults = {
        'active': True,
    }

    _order = 'code'

    _sql_constraints = [
        ('code_uniq', 'unique(code)', _("No pueden existir dos procedimientos con el mismo código!")),
        ('name_uniq', 'unique(name)', _("No pueden existir dos procedimientos con el mismo nombre!"))
    ]

    @api.one
    @api.depends('code', 'name')
    def _compute_display_name(self):
        self.display_name = '%s - %s' % (self.code, self.name)
        
    def _search_display_name(self, operator, value):
        return ['|', ('name', operator, value), ('code', operator, value)]
    