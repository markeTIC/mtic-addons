# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields, api, _

import datetime
import logging
from dateutil.relativedelta import relativedelta

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
    start_date = fields.Date('Fecha inicio')
    end_date = fields.Date('Fecha fin')
    last_date = fields.Date('Fecha último lanzamiento')
    next_date = fields.Date('Fecha próximo lanzamiento')
    notes = fields.Text('Notas')
    active = fields.Boolean('Registro activo')
    maintenance_order_ids = fields.One2many('sigma2.maintenance.order', 'action_planning_id', string='Órdenes generadas')

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

    @staticmethod
    def _get_next_date(date, unit, interval):
        """
        Get the date that results on incrementing given date an interval of time in time unit.
        @param date: Original date.
        @param unit: Interval time unit.
        @param interval: Quantity of the time unit.
        @rtype: date
        @return: The date incremented in 'interval' units of 'unit'.
        """
        if unit == 'day':
            return date + datetime.timedelta(days=interval)
        elif unit == 'week':
            return date + datetime.timedelta(weeks=interval)
        elif unit == 'month':
            return date + relativedelta(months=interval)
        elif unit == 'year':
            return date + relativedelta(years=interval)

#    def do_generate_preventive(self, cr, uid, group='A', context=None):
#        """ Generar las órdenes de preventivo pendientes para el grupo indicado """
#        _logger.info("Generando preventivo para el grupo: %s", group)
#        ids = self.search(cr, uid, [('group', '=', group),
#                                    ('active', '=', True)],
#                                #    ('next_date', '<=', datetime.date.today().strftime('%Y-%m-%d'))],
#                                # ('last_date', '<', next_date)],
#                          context=context)
#        if ids:
#            self.generate_preventive(cr, uid, ids, context=context)

    @api.model
    def do_generate_preventive(self, group='A'):
        """ Generar las órdenes de preventivo pendientes para el grupo indicado """
        _logger.info("Generando preventivo para el grupo: %s", group)
        ids = self.search([('group', '=', group), ('active', '=', True)])
        if not ids:
            return

        for action_planning in ids:
            _logger.info("Generando preventivo para: %s", action_planning.name)
            if action_planning.end_date and fields.Date.from_string(action_planning.end_date) < datetime.date.today():
                # si tiene fecha de fin, y se ha alcanzado
                _logger.debug("Se ha alcanzado la fecha de fin %s", action_planning.end_date)
                continue
            if not action_planning.asset_id.active:
                # si la máquina no está activa (registro)
                _logger.debug("La maquina no existe (registro desactivado)")
                continue
            if action_planning.asset_id.status != "active":
                # si la máquina no está en servicio
                _logger.debug("La maquina no esta en servicio (%s)", action_planning.asset_id.status)
                continue

            _logger.info("procesar %s", action_planning.name)
            today = datetime.date.today()
            next_date = False
            iterations = 0
            if not action_planning.next_date:
                if action_planning.start_date:
                    next_date = fields.Date.from_string(action_planning.start_date)
            else:
                next_date = fields.Date.from_string(action_planning.next_date)

            while next_date and next_date <= today and iterations < 10:
                # si hay varias órdenes pendientes de generar en la misma gama, se generan todas (hasta un máximo de 10)
                asset_level1, asset_level2, asset_level3 = False, False, False
                asset_level1 = action_planning.asset_id
                if action_planning.asset_id.parent_id:
                    asset_level1 = action_planning.asset_id.parent_id
                    asset_level2 = action_planning.asset_id
                if action_planning.asset_id.parent_id.parent_id:
                    asset_level1 = action_planning.asset_id.parent_id.parent_id
                    asset_level2 = action_planning.asset_id.parent_id
                    asset_level3 = action_planning.asset_id
                new_mo = self.env['sigma2.maintenance.order'].create({
                    'order_type_id': action_planning.order_type_id.id,
                    'code': self.pool.get('ir.sequence').next_by_id(self._cr, self._uid, action_planning.order_type_id.counter.id, context={}),
                    'date': next_date,
                    'origin_employee_id': self.env.uid,
                    'asset_level1': asset_level1 and asset_level1.id,
                    'asset_level2': asset_level2 and asset_level2.id,
                    'asset_level3': asset_level3 and asset_level3.id,
                    'asset_id': action_planning.asset_id.id,
                    'description': action_planning.procedure_id.name + ' Instr. %s' % action_planning.instruction,
                    'action_planning_id': action_planning.id
                })
                _logger.info("generada orden %s para %s", new_mo.code, new_mo.asset_id.name)
                iterations += 1
                last_date = next_date
                next_date = sigma2_action_planning._get_next_date(next_date, action_planning.period_type,
                                                                  action_planning.period_number)
                _logger.info("proxima fecha de lanzamiento %s", next_date.strftime('%d/%m/%Y'))
                action_planning.write({'last_date': last_date, 'next_date': next_date})

