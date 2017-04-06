# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp.osv import osv
from openerp.report import report_sxw

import time
import logging

_logger = logging.getLogger(__name__)


class maintenance_order_list(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(maintenance_order_list, self).__init__(cr, uid, name, context=context)
        self.list_type = False
        self.from_date = False
        self.to_date = False
        self.origin_employee_id = False
        self.assigned_employee_id = False
        self.status = False
        self.stop_time = False
        self.asset_line_id = False
        self.asset_id = False
        self.localcontext.update({
            'time': time,
            'get_orders': self._get_orders,
        })

    def _get_orders(self, form):
        self.list_type = form['list_type']
        self.from_date = form['from_date']
        self.to_date = form['to_date']
        self.status = form['status']
        self.origin_employee_id = form['origin_employee_id']
        self.assigned_employee_id = form['assigned_employee_id']
        self.asset_line_id = form['asset_line_id']
        self.asset_id = form['asset_id']
        self.stop_time = form['stop_time']

        domain = [('order_type_id.type', '=', self.list_type), ('date', '>=', self.from_date),
                  ('date', '<=', self.to_date)]

        status = []
        if self.list_type == 'P':
            if self.status == 'closed':
                status = ['finished', 'closed']
            elif self.status == 'pending':
                status = ['pending', 'stop', 'planned', 'open', 'parts', 'scaled']
            elif self.status == 'all':
                status = ['pending', 'stop', 'planned', 'open', 'parts', 'scaled', 'finished', 'closed']
        else:
            if self.status == 'closed':
                status = ['closed']
            elif self.status == 'pending':
                status = ['pending', 'stop', 'planned', 'open', 'parts', 'scaled', 'finished']
            elif self.status == 'all':
                status = ['pending', 'stop', 'planned', 'open', 'parts', 'scaled', 'finished', 'closed']
        domain.append(('state', 'in', status))

        if self.origin_employee_id:
            domain.append(('origin_employee_id.id', '=', self.origin_employee_id))

        if self.assigned_employee_id:
            domain.append(('assigned_employee_id.id', '=', self.asset_line_id))

        if self.asset_line_id:
            domain.append(('asset_level1.id', '=', self.asset_line_id))

        if self.asset_id:
            domain.append(('asset_id.id', '=', self.asset_line_id))

        if self.stop_time == 'yes':
            domain.append(('stop_time', '>', 0))
        elif self.stop_time == 'no':
            domain.append(('stop_time', '=', 0))

        order_ids = self.pool.get('sigma2.maintenance.order').search(
            self.cr, self.uid, domain,
            # order='asset_level1.code, asset_id.code', - por defecto ya está ordenado por código
            context=self.localcontext)

        orders = []
        for order in self.pool.get('sigma2.maintenance.order').browse(
                self.cr, self.uid, order_ids, context=self.localcontext):
            data = {'code': order.code, 'state': order.state, 'date': order.date,
                    'description': order.description, 'solution_description': order.solution_description,
                    'end_date': order.end_date, 'repair_time': order.repair_time, 'stop_time': order.stop_time,
                    'stop_time_rated': order.stop_time_rated, 'notes': order.notes, 'work_shift': order.work_shift,
                    'asset_level1': order.asset_level1.display_name, 'asset_id': order.asset_id.display_name,
                    'origin_employee_id': order.origin_employee_id.display_name}
            if order.worker_ids:
                workers = {}
                for w in order.worker_ids:
                    if w.employee_id.display_name in workers.keys():
                        work_time = workers[w.employee_id.display_name]['work_time']
                        workers[w.employee_id.display_name]['work_time'] = work_time + w.work_time
                    else:
                        workers[w.employee_id.display_name] = {'employee_id': w.employee_id.display_name, 'work_time': w.work_time}
                data['worker_ids'] = workers
            else:
                data['worker_ids'] = False
            if order.part_ids:
                parts = []
                for p in order.part_ids:
                    parts.append({'barcode': p.product_id.barcode, 'description': p.description, 'qty': p.qty})
                data['part_ids'] = parts
            else:
                data['part_ids'] = False
            orders.append(data)

        _logger.warn("orders=%s", orders)

        return orders


class report_maintenance_order_list(osv.AbstractModel):
    _name = 'report.sigma2.report_maintenance_order_list'
    _inherit = 'report.abstract_report'
    _template = 'sigma2.report_maintenance_order_list'
    _wrapped_report_class = maintenance_order_list
