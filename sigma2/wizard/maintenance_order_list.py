# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp.osv import fields, osv
import logging

_logger = logging.getLogger(__name__)


class sigma2_maintenance_order_list(osv.osv_memory):
    _name = 'sigma2.maintenance_order_list'
    _description = 'Maintenance Order List'

    _columns = {
        'list_type': fields.selection([('C', 'Correctivo'), ('P', 'Preventivo'), ('L', 'Legal (insp. reglamentarias)')], 'Tipo de listado', required=True),
        'from_date': fields.date('Desde fecha', required=True),
        'to_date': fields.date('Hasta fecha', required=True),
        'asset_line_id': fields.many2one('sigma2.asset', 'Línea',
                                      domain="[('status', '=', 'active'), ('asset_type_id.type', '=', 'line'), ]"),
        'asset_id': fields.many2one('sigma2.asset', 'Máquina',
                                 domain="[('status', '=', 'active'), ]"),
        'status': fields.selection([('closed', 'Realizadas'), ('pending', 'No realizadas'), ('all', 'Todas')], 'Estado'),
        'stop_time': fields.selection([('yes', 'Con tiempo de paro'), ('no', 'Sin tiempo de paro'), ('all', 'Todas')], 'Tiempo de paro'),
        'origin_employee_id': fields.many2one('hr.employee', 'Solicitante'),
        'assigned_employee_id': fields.many2one('hr.employee', 'Operario (asignado)')
    }

    def onchange_asset_line(self, cr, uid, ids, asset_line_id=False, context=None):
        res = {}
        if asset_line_id:
            res['domain'] = {'asset_id': [('status', '=', 'active'), ('parent_id', '!=', False), ('parent_id', '=', asset_line_id)]}
            res['value'] = {'asset_id': False, 'asset_line_id': asset_line_id}
        else:
            res['domain'] = {'asset_id': [('status', '=', 'active'), ('asset_type_id.type', '=', 'line'), ]}
            res['value'] = {'asset_id': False, 'asset_line_id': asset_line_id}
        return res

    def print_report(self, cr, uid, ids, context=None):
        """
        To get the date and print the report
        @return : return report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['list_type', 'from_date', 'to_date', 'asset_line_id', 'asset_id', 'status',
                                       'stop_time', 'origin_employee_id', 'assigned_employee_id'], context=context)
        res = res and res[0] or {}
        res['asset_line_id_name'] = res['asset_line_id'] and res['asset_line_id'][1]
        res['asset_line_id'] = res['asset_line_id'] and res['asset_line_id'][0]
        res['asset_id_name'] = res['asset_id'] and res['asset_id'][1]
        res['asset_id'] = res['asset_id'] and res['asset_id'][0]
        res['origin_employee_id_name'] = res['origin_employee_id'] and res['origin_employee_id'][1]
        res['origin_employee_id'] = res['origin_employee_id'] and res['origin_employee_id'][0]
        res['assigned_employee_id_name'] = res['assigned_employee_id'] and res['assigned_employee_id'][1]
        res['assigned_employee_id'] = res['assigned_employee_id'] and res['assigned_employee_id'][0]

        datas['form'] = res
        _logger.warn("datas['form']=%s", res)
        return self.pool['report'].get_action(cr, uid, [], 'sigma2.report_maintenance_order_list', data=datas, context=context)

    _defaults = {
        'list_type': 'C',
        'from_date': fields.date.today(),
        'to_date': fields.date.today(),
        'status': 'all',
        'stop_time': 'all',
    }

