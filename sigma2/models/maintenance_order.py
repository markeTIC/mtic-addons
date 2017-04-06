# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime

import logging

_logger = logging.getLogger(__name__)


class sigma2_maintenance_order(models.Model):
    """Orden de mantenimiento"""
    _name = 'sigma2.maintenance.order'
    _description = 'Maintenance Order'
    _inherit = ['mail.thread']

    order_type_id = fields.Many2one('sigma2.order.type', 'Tipo de orden', required=True, select=True,
                                    ondelete='restrict', readonly=True, states={'pending': [('readonly', False)]})
    code = fields.Char('Número', required=True, select=True, readonly=True, states={'pending': [('readonly', False)]})
    date = fields.Datetime('Fecha', required=True, readonly=True, states={'pending': [('readonly', False)]})
    work_shift = fields.Selection(
        selection=[
            ('1', '1'),
            ('2', '2'),
            ('3', '3'),
        ],
        required=False,
        string='Turno',
        default='1', readonly=True, states={'pending': [('readonly', False)]})
    origin_employee_id = fields.Many2one('hr.employee', 'Solicitado por', required=True, ondelete='restrict',
                                         readonly=True, states={'pending': [('readonly', False)]})
    origin_department_id = fields.Many2one('hr.department', 'Departamento', compute="_compute_origin_department_id",
                                           store=True, select=True, ondelete='restrict',
                                           readonly=True, states={'pending': [('readonly', False)]})
    state = fields.Selection(
        selection=[
            ('pending', 'Pendiente'),
            ('stop', 'Paro'),
            ('planned', 'Planificada'),
            ('open', 'En curso'),
            ('parts', 'Pdte. repuestos'),
            ('scaled', 'Pdte. terceros'),
            ('finished', 'Finalizada'),
            ('closed', 'Cerrada'),
            ('canceled', 'Cancelada'),
        ],
        required=True,
        track_visibility='onchange',
        string='Estado',
        default='pending')
    state_date = fields.Datetime('Fecha estado')
    state_note = fields.Char('Motivo estado')
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
        track_visibility='onchange',
        string='Prioridad',
        default='B')
    description = fields.Text('Descripción', required=True)
    solution_description = fields.Text('Solución')
    asigned_employee_id = fields.Many2one('hr.employee', 'Asignada a', select=True, ondelete='restrict', track_visibility='onchange')
    planned_date = fields.Datetime('Fecha prevista')
    start_date = fields.Date('Fecha inicio reparación', readonly=True)
    end_date = fields.Date('Fecha fin reparación', readonly=True)
    repair_time = fields.Integer('Tiempo reparación (minutos)', readonly=True)
    stop_time = fields.Integer('Tiempo paro máquina (minutos)')
    stop_time_rated = fields.Integer('Tiempo paro producción (minutos)')
    authorization_employee_id = fields.Many2one('hr.employee', 'Autorizado por', select=True, ondelete='restrict', domain="[('user_id.id', '=', uid)]", track_visibility='onchange')
    notes = fields.Text('Notas')
    active = fields.Boolean('Registro activo')
    display_name = fields.Char('Orden de mantenimiento', compute='_compute_display_name', search='_search_display_name', readonly=True)
    worker_ids = fields.One2many('sigma2.maintenance.order.worker', 'maintenance_order_id', string='Trabajadores de la orden', states={'finished': [('readonly', True)], 'closed': [('readonly', True)]})
    part_ids = fields.One2many('sigma2.maintenance.order.part', 'maintenance_order_id', string='Recambios de la orden', states={'finished': [('readonly', True)], 'closed': [('readonly', True)]})
    action_planning_id = fields.Many2one('sigma2.action.planning', 'Gama preventivo', ondelete='restrict', readonly=True)
    color_index = fields.Integer('Color de la orden', compute='_compute_color_index', store=False)
    validation_employee_id = fields.Many2one('hr.employee', 'Validado por', select=True, ondelete='restrict', domain="[('user_id.id', '=', uid)]", readonly=True, track_visibility='onchange')
    speciality_id = fields.Many2one('sigma2.speciality', 'Especialidad', select=True, ondelete='restrict')
    company_id = fields.Many2one('res.company', 'Empresa')
    # Campos para órdenes de calibración
    calibration_date = fields.Date('Fecha calibración')
    next_calibration_date = fields.Date('Fecha prox. calibración')
    calibrator_id = fields.Many2one('res.partner', 'Calibrador', ondelete='restrict')
    calibration_certificate_number = fields.Char('Núm. certificado')
    # Campos para la vista
    # creamos un campo para pasar un parámetro que indique el tipo de orden a crear
    param_order_type_code = fields.Char('Código tipo de orden (parámetro para las vistas)', store=False, readonly=True, search='_search_param_order_type_code')
    # creamos un campo para evitar un bucle en los on_change si se establece la maquina por un valor por defecto
#    param_asset_id = fields.Many2one('sigma2.asset', 'Máquina (parámetro para las vistas)', store=False, readonly=True)
# Si se añade este campo da error:
# _description_searchable" while parsing /opt/odoo/mtic-addons/sigma2/views/action_planning.xml:33, near
    # hacemos el campo create_date visible para poder usarlo en la vista, para ocultar pestañas en la creación del registro
    create_date = fields.Date('Fecha creación', invisible=False, readonly=True)
    # creamos un campo para filtrar las órdenes de preventivo por listado de línea y fecha
    preventive_barcode = fields.Char('Código preventivo', compute='_compute_preventive_barcode', store=True, readonly=True)
    ##
    order_type_id_type = fields.Selection('Tipo de orden (clave de tipo)', related='order_type_id.type')

    _rec_name = 'display_name'
    
    _defaults = {
        'active': True,
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

    @api.one
    @api.depends('priority', 'state')
    def _compute_color_index(self):

        if self.state == 'stop':
            self.color_index = 1  # red
        else:
            if self.state == 'pending' or self.state == 'planned':
                self.color_index = 3  # blue
            elif self.state == 'open':
                self.color_index = 6  # green
            elif self.state == 'parts' or self.state == 'scaled':
                self.color_index = 7  # purple
            else:
                self.color_index = 0  # black

            if self.priority == 'A':
                if self.state == 'pending' or self.state == 'planned':
                    self.color_index = 1  # red
                elif self.state == 'open':
                    self.color_index = 2  # orange
                elif self.state == 'parts' or self.state == 'scaled':
                    self.color_index = 8  # magenta
                else:
                    self.color_index = 0  # black
            if self.priority == 'C':
                if self.state == 'pending' or self.state == 'planned':
                    self.color_index = 5  # grey
                elif self.state == 'open':
                    self.color_index = 4  # lightgreen
                else:
                    self.color_index = 0  # black

    @api.onchange('param_order_type_code')
    def _param_order_type_code_onchange(self):
        if self.param_order_type_code:
            order_type_rs = self.env['sigma2.order.type'].search([('code', '=', self.param_order_type_code)])
            if order_type_rs:
                self.order_type_id = order_type_rs[0]

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
        self.date = fields.datetime.now()
        # domain = {'origin_employee_id': [('user_id', '=', self.env.uid)], 'asigned_employee_id': [('user_id', '=', self.env.uid)]}
        # return {'domain': domain}

    @api.one
    @api.depends('origin_employee_id')
    def _compute_origin_department_id(self):
        if self.origin_employee_id:
            self.origin_department_id = self.origin_employee_id.department_id
        else:
            self.origin_department_id = None
    
    @api.one
    @api.depends('date', 'asset_level1')
    def _compute_preventive_barcode(self):
        if self.order_type_id and self.order_type_id.type == 'P' and self.date and self.asset_level1:
            self.preventive_barcode = "%s-%s" % (fields.Datetime.from_string(self.date).strftime('%y%m%d'),
                                                 self.asset_level1.code)
        else:
            self.preventive_barcode = False

    @api.onchange('planned_date')
    def _planned_date_onchange(self):
        if self.planned_date and self.state == 'pending':
            self.state = 'planned'

#    @api.onchange('param_asset_id')
    def _param_asset_id_onchange(self):
        if self.param_asset_id:
            if not self.asset_level1:
                if not self.param_asset_id.parent_id:
                    self.asset_level1 = self.param_asset_id
                    self.asset_id = self.param_asset_id
                    return  # {'value': None}
                else:
                    if self.param_asset_id.parent_id.asset_type_id.type == 'line' or not self.param_asset_id.parent_id.parent_id:
                        self.asset_level1 = self.param_asset_id.parent_id
                        self.asset_level2 = self.param_asset_id
                        self.asset_id = self.param_asset_id
                        return  # {'value': None}
                    else:
                        if self.param_asset_id.parent_id.parent_id:
                            self.asset_level1 = self.param_asset_id.parent_id.parent_id
                            self.asset_level2 = self.param_asset_id.parent_id
                            self.asset_level3 = self.param_asset_id
                            self.asset_id = self.param_asset_id
                            return  # {'value': None}

    @api.onchange('asset_level1')
    def _asset_level1_onchange(self):
#        if self.param_asset_id:
#            return
        self.asset_level2 = None
        self.asset_level3 = None
        self.asset_id = self.asset_level1
        if self.order_type_id.code == 'C':
            return {'domain': {'asset_level2': [('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level1.id), '|', ('asset_type_id.type', '=', 'line'), ('asset_type_id.corrective', '=', True), ]}}
        elif self.order_type_id.code == 'P':
            return {'domain': {'asset_level2': [('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level1.id), '|', ('asset_type_id.type', '=', 'line'), ('asset_type_id.preventive', '=', True), ]}}
        elif self.order_type_id.code == 'L':
            return {'domain': {'asset_level2': [('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level1.id), '|', ('asset_type_id.type', '=', 'line'), ('regulatory_inspection', '=', True), ]}}
        elif self.order_type_id.code == 'CAL':
            return {'domain': {'asset_level2': [('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level1.id), '|', ('asset_type_id.type', '=', 'line'), ('calibration', '=', True), ]}}
        else:
            return {'domain':{'asset_level2': [('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level1.id), ]}}

    @api.onchange('asset_level2')
    def _asset_level2_onchange(self):
 #       if self.param_asset_id:
 #           return
        self.asset_level3 = None
        if self.asset_level2:
            self.asset_id = self.asset_level2
        else:
            self.asset_id = self.asset_level1
        if self.order_type_id.code == 'C':
            return {'domain': {'asset_level3': [('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level2.id), '|', ('asset_type_id.type', '=', 'line'), ('asset_type_id.corrective', '=', True), ]}}
        elif self.order_type_id.code == 'P':
            return {'domain': {'asset_level3': [('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level2.id), '|', ('asset_type_id.type', '=', 'line'), ('asset_type_id.preventive', '=', True), ]}}
        elif self.order_type_id.code == 'L':
            return {'domain': {'asset_level3': [('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level2.id), '|', ('asset_type_id.type', '=', 'line'), ('regulatory_inspection', '=', True), ]}}
        elif self.order_type_id.code == 'CAL':
            return {'domain': {'asset_level3': [('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level2.id), '|', ('asset_type_id.type', '=', 'line'), ('calibration', '=', True), ]}}
        else:
            return {'domain': {'asset_level3': [('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', self.asset_level2.id), ]}}
    
    @api.onchange('asset_level3')
    def _asset_level3_onchange(self):
#        if self.param_asset_id:
#            return
        if self.asset_level3:
            self.asset_id = self.asset_level3
        else:
            self.asset_id = self.asset_level2

    @api.onchange('asset_id')
    def _asset_id_onchange(self):
        if self.asset_id:
            if self.order_type_id.code == 'CAL':
                self.calibration_date = self.asset_id.calibration_date
                self.next_calibration_date = self.asset_id.next_calibration_date
                self.calibrator_id = self.asset_id.calibrator_id

    @api.onchange('stop_time')
    def _stop_time_onchange(self):
        if self.stop_time:
            if self.asset_id:
                self.stop_time_rated = self.stop_time * self.asset_id.computed_stop_rate / 100
            else:
                self.stop_time_rated = 0
                return {'warning': {'title': _('Atención!'), 'message': _('Debe indicar la máquina para poder calcular el tiempo de paro de producción')}}
        else:
            self.stop_time_rated = 0

    @api.multi
    def reset_order(self):
        """Vuelve la orden al estado "Pendiente" (pending), desde "Planificada" y "En curso" (planned y open)"""
        self.ensure_one()
        self.state_date = fields.datetime.now()
        return self.write({'state': 'pending'})

    @api.multi
    def open_order(self):
        """Establece la orden al estado "En curso" (open)"""
        self.ensure_one()
        self.state_date = fields.datetime.now()
        self.start_date = fields.datetime.now()

        employee = None
        employees = self.env['res.users'].search([('id', '=', self.env.uid)])[0].employee_ids
        if len(employees) == 1:
            employee = employees[0]
            # TODO: añadir una línea con el empleado... si es necesario!

        return self.write({'state': 'open'})

    @api.multi
    def reopen_order(self):
        """Vuelve la orden al estado abierta (open), desde "Pdte. repuestos", "Pdte. terceros", "Finalizada",
        "Cerrada", "Cancelada" (parts, scaled, finished, closed, canceled)
        Si no se hace nada más, puede sustituirse por la función open_order
        """
        self.ensure_one()
        self.state_date = fields.datetime.now()
        self.state = 'open'
        self.validation_employee_id = False
        return self.write

    @api.multi
    def parts_fault_order(self):
        """Establece la orden al estado "Pdte. repuestos" (parts)"""
        self.ensure_one()
        self.state_date = fields.datetime.now()
        self.state = 'parts'
        return self.write

    @api.multi
    def scale_order(self):
        """Establece la orden al estado "Pdte. terceros" (scaled)"""
        self.ensure_one()
        self.state_date = fields.datetime.now()
        self.state = 'scaled'
        return self.write

    @api.multi
    def finish_order(self):
        """Finaliza la orden (finished)"""
        self.ensure_one()
        self.state_date = fields.datetime.now()
        self.state = 'finished'
        total_time = 0
        start_date = None
        end_date = None
        for worker in self.worker_ids:
            total_time = total_time + worker.work_time
            if not start_date or (datetime.strptime(worker.start_date, DEFAULT_SERVER_DATE_FORMAT) <
                                  datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)):
                start_date = worker.start_date
            if not end_date or (datetime.strptime(worker.start_date, DEFAULT_SERVER_DATE_FORMAT) >
                                datetime.strptime(end_date, DEFAULT_SERVER_DATE_FORMAT)):
                end_date = worker.start_date
        self.repair_time = total_time
        self.start_date = start_date
        self.end_date = end_date
        return self.write

    @api.multi
    def validate_order(self):
        """Valida la orden por parte del responsable.
        Establece el estado closed."""
        self.ensure_one()
        employee = None
        employees = self.env['res.users'].search([('id', '=', self.env.uid)])[0].employee_ids
        if len(employees) == 1:
            employee = employees[0]
        self.state_date = fields.datetime.now()
        self.state = 'closed'
        self.validation_employee_id = employee
        if self.order_type_id.code == 'CAL':
            self.asset_id.calibration_date = self.calibration_date
            self.asset_id.next_calibration_date = self.next_calibration_date
        return self.write

    @api.multi
    def cancel_order(self):
        """Cancela la orden"""
        self.ensure_one()
        self.state_date = fields.datetime.now()
        self.state = 'canceled'
        return self.write

    @api.multi
    def asset_stop(self):
        """Máquina parada"""
        self.ensure_one()
        self.state = 'stop'
        return self.write

    @api.multi
    def asset_start(self):
        """Máquina en marcha"""
        self.ensure_one()
        self.state = 'pending'
        return self.write

    @api.model
    def create(self, vals):
        res = super(sigma2_maintenance_order, self).create(vals)
        return res

    @api.multi
    def write(self, vals):
        if self.order_type_id.type == 'C':
            if self.state == 'pending' and 'state' in vals and vals['state'] == 'stop':
                template = self.env.ref('sigma2.email_template_maintenance_order_stop')
                template.send_mail(self.id, force_send=True, context=self.env.context)
            if self.state == 'stop' and 'state' in vals and vals['state'] != 'stop':
                template = self.env.ref('sigma2.email_template_maintenance_order_run')
                template.send_mail(self.id, force_send=True, context=self.env.context)
        return super(sigma2_maintenance_order, self).write(vals)

#    @api.multi
#    def message_auto_subscribe(self, updated_fields, context=None, values=None):
#        _logger.warn('message_auto_subscribe ---------> %s', updated_fields)
#        return super(sigma2_maintenance_order, self).message_auto_subscribe(updated_fields, context=context, values=values)


class sigma2_maintenance_order_worker(models.Model):
    """Trabajador de la orden de mantenimiento"""

    _name = 'sigma2.maintenance.order.worker'
    _description = 'Maintenance Order Worker'
    
    maintenance_order_id = fields.Many2one('sigma2.maintenance.order', 'Orden de mantenimiento', required=True, select=True, ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', 'Trabajador', required=True, ondelete='restrict')
    start_date = fields.Date('Fecha inicio', required=True)
    work_time = fields.Integer('Tiempo (minutos)', required=True)
    active = fields.Boolean('Registro activo')

    _defaults = {
        'active': True,
    }

    _order = 'start_date'

    @api.onchange('active')
    def _active_onchange(self):
        # al iniciar la edición de la linea...
        # establecemos el trabajador (y su filtro) y la fecha
        employees = self.env['res.users'].search([('id', '=', self.env.uid)])[0].employee_ids
        if len(employees) == 1:
            self.employee_id = employees[0]
        self.start_date = fields.date.today()
#        domain = {'employee_id':[('user_id', '=', self.env.uid)]}
#        return {'domain': domain}


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
