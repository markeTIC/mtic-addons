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

class sigma2_action_planning(models.Model):
    """Planificación gamas de mantenimiento"""

    _name = 'sigma2.action.planning'
    _description = 'Maintenance Action Planning'

    name = fields.Char(compute='_compute_name',)
    procedure_id = fields.Many2one('sigma2.procedure', 'Procedimiento', select=True, ondelete='restrict')
    instruction = fields.Char('Instrucción')
    order_type_id = fields.Many2one('sigma2.order.type', 'Tipo de orden', select=True, ondelete='restrict')
    asset_id = fields.Many2one('sigma2.asset', 'Activo mantenimiento', select=True, ondelete='restrict',
                                domain="[('status', '=', 'active'), ('asset_type_id.preventive', '=', True), ]")
    period_type = fields.Selection(
        selection=[
            ('year', 'Año'),
            ('month', 'Mes'),
            ('week', 'Semana'),
            ('day', 'Día'),
        ],
        required=True,
        string='Periodo')
    period_number = fields.Integer('Número periodos')
    group = fields.Char('Grupo', required=True)
    start_date = fields.Datetime('Fecha inicio')
    end_date = fields.Datetime('Fecha fin')
    last_date = fields.Datetime('Fecha último lanzamiento')
    next_date = fields.Datetime('Fecha próximo lanzamiento')
    notes = fields.Text('Notas')
    active = fields.Boolean('Registro activo')

    _defaults = {
        'active': True,
        'period_type': 'month',
        'group': 'A',
    }

    _order = 'asset_id, procedure_id, instruction'

    @api.one
    @api.depends('asset_id', 'procedure_id')
    def _compute_name(self):
        self.name = '%s / %s - %s' % (self.asset_id.name, self.procedure_id.code, self.procedure_id.name)
        
