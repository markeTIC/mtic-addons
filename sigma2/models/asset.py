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

class sigma2_asset(models.Model):
    """Activos para mantenimiento"""

    _name = 'sigma2.asset'
    _description = 'Maintenance Asset'

    code = fields.Char('Código', required=True, select=True)
    name = fields.Char('Nombre', required=True, select=True)
    asset_type_id = fields.Many2one('sigma2.asset.type', 'Tipo de activo', select=True, ondelete='restrict')
    asset_class_id = fields.Many2one('sigma2.asset.class', 'Clase de activo', select=True, ondelete='restrict')
    status = fields.Selection(
        selection=[
            ('active', 'Activo'),
            ('retired', 'Retirado')
        ],
        required=True,
        string='Estado',
        default='active')
    reference = fields.Char('Referencia')
    serial_number = fields.Char('Número de serie')
    parent_id = fields.Many2one('sigma2.asset', 'Activo padre', select=True, ondelete='restrict')
    child_ids = fields.One2many('sigma2.asset', 'parent_id', string='Activos hijos')
    location_id = fields.Many2one('sigma2.location', 'Zona de fábrica', ondelete='set null')
    stop_rate = fields.Integer('Afectación paro producción (%)')
    action_planning_ids = fields.One2many('sigma2.action.planning', 'asset_id', string='Gamas del activo')
    regulatory_inspection = fields.Boolean('Inspección reglamentaria', 
                                           compute='_compute_regulatory_inspection', 
                                           search='_search_regulatory_inspection')
    applicable_regulations = fields.Char('Reglamento aplicable', 
                                         compute='_compute_applicable_regulations', 
                                         search='_search_applicable_regulations')
    notes = fields.Text('Notas')
    active = fields.Boolean('Registro activo')
    display_name = fields.Char('Activo', compute='_compute_display_name', search='_search_display_name',)

    _rec_name = 'display_name'
    
    _defaults = {
        'active': True,
        'stop_rate': 100,
    }

    _order = 'code'

    @api.one
    @api.depends('code', 'name')
    def _compute_display_name(self):
        self.display_name = '%s - %s' % (self.code, self.name)
        
    def _search_display_name(self, operator, value):
        return ['|', ('name', operator, value), ('code', operator, value)]
    
    @api.one
    @api.depends('asset_class_id')
    def _compute_regulatory_inspection(self):
        if self.asset_class_id:
            self.regulatory_inspection = self.asset_class_id.regulatory_inspection
        else:
            self.regulatory_inspection = False

    def _search_regulatory_inspection(self, operator, value):
        return [('asset_class_id.regulatory_inspection', operator, value)]
        
    @api.one
    @api.depends('asset_class_id')
    def _compute_applicable_regulations(self):
        if self.asset_class_id:
            self.applicable_regulations= self.asset_class_id.applicable_regulations
        else:
            self.applicable_regulations = False

    def _search_applicable_regulations(self, operator, value):
        return [('asset_class_id.applicable_regulations', operator, value)]
        
        
class sigma2_asset_counter(models.Model):
    """Contador de activo para mantenimiento"""

    _name = 'sigma2.asset.counter'
    _description = 'Maintenance Asset Counter'

    name = fields.Char('Nombre', required=True, select=True)
    asset_id = fields.Many2one('sigma2.asset', 'Activo', select=True, ondelete='cascade')
    current_value = fields.Integer('Valor actual')
    active = fields.Boolean('Registro activo')

    _defaults = {
        'active': True,
    }

    _order = 'name'
