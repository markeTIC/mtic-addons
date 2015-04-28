# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import SUPERUSER_ID
from openerp import models, fields, api, _

from datetime import date
import logging
import time
from docutils.nodes import description

_logger = logging.getLogger(__name__)

class sigma2_maintenance_order(models.Model):
    """Orden de mantenimiento"""

    _name = 'sigma2.maintenance.order'
    _description = 'Maintenance Order'
    
    order_type_id = fields.Many2one('sigma2.order.type', 'Tipo de orden', required=True, select=True, ondelete='restrict')
    code = fields.Char('Número', required=True, select=True)
    date = fields.Date('Fecha', required=True)
    hour = fields.Integer('Hora')
    work_shift = fields.Integer('Turno')
    origin_employee_id = fields.Many2one('hr.employee', 'Solicitado por', required=True, ondelete='restrict')
    origin_department_id = fields.Many2one('hr.department', 'Departamento', compute="_compute_origin_department_id", store=True, select=True, ondelete='restrict')
    status = fields.Selection(
        selection=[
            ('pending', 'Pendiente'),
            ('planned', 'Planificada'),
            ('open', 'En curso'),
            ('finished', 'Finalizada'),
            ('canceled', 'Cancelada'),
            ('rejected', 'Rechazada'),
        ],
        required=True,
        string='Estado',
        default='pending')
    status_date = fields.Datetime('Fecha estado')
    status_note = fields.Char('Motivo estado')
    asset_id = fields.Many2one('sigma2.asset', 'Máquina', required=True, select=True, ondelete='restrict')
    asset_level1 = fields.Many2one('sigma2.asset', 'Línea', required=True, domain="[('status', '=', 'active'), ('asset_type_id.type', '=', 'line'), ]")
    asset_level2 = fields.Many2one('sigma2.asset', 'Línea / Máquina', domain="[('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', asset_level1), ]")
    asset_level3 = fields.Many2one('sigma2.asset', 'Máquina', domain="[('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', asset_level2), ]")
    priority = fields.Selection(
        selection=[
            ('A', 'Urgente'),
            ('B', 'Normal'),
            ('C', 'Baja'),
        ],
        required=True,
        string='Prioridad',
        default='B')
    description = fields.Text('Descripción', required=True)
    solution_description = fields.Text('Solución')
    asigned_employee_id = fields.Many2one('hr.employee', 'Asignada a', select=True, ondelete='restrict')
    planned_date = fields.Datetime('Fecha prevista')
    start_date = fields.Datetime('Fecha inicio reparación')
    end_date = fields.Datetime('Fecha fin reparación')
    repair_time = fields.Integer('Tiempo reparación (minutos)')
    stop_time = fields.Integer('Tiempo paro máquina (minutos)')
    stop_time_rated = fields.Integer('Tiempo paro producción (minutos)')
    authorization_employee_id = fields.Many2one('hr.employee', 'Autorizado por', select=True, ondelete='restrict')
    notes = fields.Text('Notas')
    active = fields.Boolean('Registro activo')
    display_name = fields.Char('Orden de mantenimiento', compute='_compute_display_name', search='_search_display_name', readonly=True)
    worker_ids = fields.One2many('sigma2.maintenance.order.worker', 'maintenance_order_id', string='Trabajadores de la orden')
    part_ids = fields.One2many('sigma2.maintenance.order.part', 'maintenance_order_id', string='Recambios de la orden')
    action_planning_id = fields.Many2one('sigma2.action.planning', 'Gama prev.', ondelete='restrict', readonly=True)
    # Campos para la vista
    # creamos un campo para pasar un parámetro que indique el tipo de orden a crear
    param_order_type_code = fields.Char('Código tipo de orden (parámetro para las vistas)', store=False, readonly=True, search='_search_param_order_type_code')
    # hacemos el campo create_date visible para poder usarlo en la vista, para ocultar pestañas en la creación del registro
    create_date = fields.Date('Fecha creación', invisible=False, readonly=True,)
    ##
    
    _rec_name = 'display_name'
    
    _defaults = {
        'active': True,
        'date': fields.date.today(),
    }

    _order = 'code'

    _sql_constraints = [
        ('code_uniq', 'unique(code)', _("No pueden existir dos órdenes con el mismo código!")),
    ]

    @api.one
    @api.depends('code')
    def _compute_display_name(self):
        self.display_name = self.code
        
    def _search_display_name(self, operator, value):
        return [('code', operator, value),]

    def _search_param_order_type_code(self, operator, value):
        # TODO: Corregir!
        return [('code', operator, value)]

    @api.onchange('param_order_type_code')
    def _param_order_type_code_onchange(self):
        if self.param_order_type_code:
            self.order_type_id = self.env.ref('sigma2.order_type_' + self.param_order_type_code)

    @api.onchange('order_type_id')
    def _order_type_id_onchange(self):
        if self.order_type_id and self.order_type_id.counter:
            self.code = self.pool.get('ir.sequence').next_by_id(self._cr, self._uid, self.order_type_id.counter.id, context={})
        else:
            self.code = None
        self.asset_level1 = None
        employees = self.env['res.users'].search([('id', '=', self.env.uid)])[0].employee_ids
        if len(employees) == 1:
            self.origin_employee_id = employees[0]
        domain = {'origin_employee_id':[('user_id', '=', self.env.uid)], 'authorization_employee_id':[('user_id', '=', self.env.uid)]}
        return {'domain': domain}

    @api.one
    @api.depends('origin_employee_id')
    def _compute_origin_department_id(self):
        if self.origin_employee_id:
            self.origin_department_id = self.origin_employee_id.department_id
        else:
            self.origin_department_id = None
    
    @api.onchange('status')
    def _status_onchange(self):
        self.status_date = fields.datetime.today()

    @api.onchange('planned_date')
    def _planned_date_onchange(self):
        if self.planned_date and self.status == 'pending':
            self.status = 'planned'

    @api.onchange('start_date')
    def _start_start_date(self):
        if self.start_date and (self.status == 'pending' or self.status == 'planned'):
            self.status = 'open'

    @api.onchange('end_date')
    def _end_date_onchange(self):
        if self.end_date:
            self.status = 'finished'
            if not self.start_date:
                self.start_date = self.end_date
            if not self.repair_time:
                total_time = 0
                for worker in self.worker_ids:
                    total_time = total_time + worker.work_time
                self.repair_time = total_time
        
    @api.onchange('asset_level1')
    def _asset_level1_onchange(self):
        self.asset_level2 = None
        self.asset_level3 = None
        self.asset_id = self.asset_level1
        if self.order_type_id.code == 'C':
            return {'domain':{'asset_level2':[('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level1.id), '|', ('asset_type_id.type', '=', 'line'), ('asset_type_id.corrective', '=', True), ]}}
        elif self.order_type_id.code == 'P':
            return {'domain':{'asset_level2':[('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level1.id), '|', ('asset_type_id.type', '=', 'line'), ('asset_type_id.preventive', '=', True), ]}}
        elif self.order_type_id.code == 'L':
            return {'domain':{'asset_level2':[('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level1.id), '|', ('asset_type_id.type', '=', 'line'), ('regulatory_inspection', '=', True), ]}}
        else:
            return {'domain':{'asset_level2':[('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level1.id), ]}}

    @api.onchange('asset_level2')
    def _asset_level2_onchange(self):
        self.asset_level3 = None
        if self.asset_level2:
            self.asset_id = self.asset_level2
        else:
            self.asset_id = self.asset_level1
        if self.order_type_id.code == 'C':
            return {'domain':{'asset_level3':[('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level2.id), '|', ('asset_type_id.type', '=', 'line'), ('asset_type_id.corrective', '=', True), ]}}
        elif self.order_type_id.code == 'P':
            return {'domain':{'asset_level3':[('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level2.id), '|', ('asset_type_id.type', '=', 'line'), ('asset_type_id.preventive', '=', True), ]}}
        elif self.order_type_id.code == 'L':
            return {'domain':{'asset_level3':[('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level2.id), '|', ('asset_type_id.type', '=', 'line'), ('regulatory_inspection', '=', True), ]}}
        else:
            return {'domain':{'asset_level3':[('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level2.id), ]}}
    
    @api.onchange('asset_level3')
    def _asset_level3_onchange(self):
        if self.asset_level3:
            self.asset_id = self.asset_level3
        else:
            self.asset_id = self.asset_level2

    @api.onchange('stop_time')
    def _stop_time_onchange(self):
        if self.stop_time:
            if self.asset_id:
                self.stop_time_rated = self.stop_time * self.asset_id.stop_rate / 100
            else:
                self.stop_time = 0
                return {'warning':{'title':_('Atención!'), 'message': _('Debe indicar la máquina para poder calcular el tiempo de paro de producción')}}
        else:
            self.stop_time_rated = 0

            
class sigma2_maintenance_order_worker(models.Model):
    """Trabajador de la orden de mantenimiento"""

    _name = 'sigma2.maintenance.order.worker'
    _description = 'Maintenance Order Worker'
    
    maintenance_order_id = fields.Many2one('sigma2.maintenance.order', 'Orden de mantenimiento', required=True, select=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', 'Trabajador', required=True, ondelete='restrict')
    start_date = fields.Datetime('Fecha inicio', required=True)
    work_time = fields.Integer('Tiempo (minutos)', required=True)
    active = fields.Boolean('Registro activo')

    _defaults = {
        'active': True,
        'start_date': fields.date.today(),
    }

    _order = 'start_date'

    @api.onchange('active')
    def _active_onchange(self):
        # al iniciar la edición de la linea...
        # establecemos el trabajador (y su filtro)
        employees = self.env['res.users'].search([('id', '=', self.env.uid)])[0].employee_ids
        if len(employees) == 1:
            self.employee_id = employees[0]
        domain = {'employee_id':[('user_id', '=', self.env.uid)]}
        return {'domain': domain}


class sigma2_maintenance_order_part(models.Model):
    """Recambio de la orden de mantenimiento"""

    _name = 'sigma2.maintenance.order.part'
    _description = 'Maintenance Order Part'
    
    maintenance_order_id = fields.Many2one('sigma2.maintenance.order', 'Orden de mantenimiento', required=True, select=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', 'Recambio', required=True, ondelete='restrict')
    description = fields.Char('Descripción', required=True)
    qty = fields.Integer('Cantidad', required=True)
    active = fields.Boolean('Registro activo')

    _defaults = {
        'active': True,
        'qty': 1,
    }

    @api.onchange('product_id')
    def _product_id_onchange(self):
        self.description = self.product_id.name
