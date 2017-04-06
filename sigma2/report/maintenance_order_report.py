# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp.osv import fields, osv
from openerp import tools


class maintenance_order_report(osv.osv):
    _name = "sigma2.maintenance.order.report"
    _description = "Ordenes de mantenimiento"
    _auto = False
    _columns = {
        'order_type_id': fields.many2one('sigma2.order.type', 'Tipo de orden', readonly=True),
        'date': fields.datetime('Fecha', readonly=True, help="Fecha de creacion de la orden"),
        'date_year': fields.char('Año', readonly=True, length=5),
        'date_month': fields.char('Mes', readonly=True, length=2),
        'state': fields.selection([
            ('pending', 'Pendiente'),
            ('stop', 'Paro'),
            ('planned', 'Planificada'),
            ('open', 'En curso'),
            ('parts', 'Pdte. repuestos'),
            ('scaled', 'Pdte. terceros'),
            ('finished', 'Finalizada'),
            ('closed', 'Cerrada'),
            ('canceled', 'Cancelada'),
        ], 'Estado', readonly=True),
        'asset_level1': fields.many2one('sigma2.asset', 'Línea', readonly=True),
        'asset_id': fields.many2one('sigma2.asset', 'Máquina', readonly=True),
        'location_id': fields.many2one('sigma2.location', 'Zona de fábrica', readonly=True),
        'repair_time_total': fields.integer('Tiempo reparación (minutos)', readonly=True),
        'stop_time_total': fields.integer('Tiempo paro máquina (minutos)', readonly=True),
        'stop_time_rated_total': fields.integer('Tiempo paro producción (minutos)', readonly=True),
    }
    _order = 'date desc, stop_time_total desc'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'sigma2_maintenance_order_report')
        cr.execute("""
            create or replace view sigma2_maintenance_order_report as (
                SELECT
                    min(mo.id) as id,
                    mo.order_type_id,
                    mo.date,
                    to_char(mo.date, 'YYYY') as date_year,
                    to_char(mo.date, 'MM') as date_month,
                    mo.state,
                    m.location_id,
                    mo.asset_level1,
                    mo.asset_id,
                    sum(mo.repair_time) as repair_time_total,
                    sum(mo.stop_time) as stop_time_total,
                    sum(mo.stop_time_rated) as stop_time_rated_total
                FROM sigma2_maintenance_order mo
                    left join sigma2_asset l on (mo.asset_level1 = l.id)
                    left join sigma2_asset m on (mo.asset_id = m.id)
                GROUP BY
                    mo.order_type_id,
                    mo.date,
                    mo.state,
                    mo.asset_level1,
                    m.location_id,
                    mo.asset_id
            )
        """)
