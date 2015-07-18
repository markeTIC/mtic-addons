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

class preventive_list(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(preventive_list, self).__init__(cr, uid, name, context=context)
        self.date = False
        self.asset_line = False
        self.localcontext.update({
            'time': time,
            'get_lines': self._get_lines,
        })

    def _get_lines(self, form):
        res = []
        self.date = form['date']
        self.asset_line = form['asset_line']
        preventive_code = self.date[2:4] + self.date[5:7] + self.date[8:10] + '-'
        if self.asset_line:
            line = self.pool.get('sigma2.asset').read(self.cr, self.uid, [self.asset_line], ['code', 'name'],
                                                      context=self.localcontext)[0]
            order_ids = self.pool.get('sigma2.maintenance.order').search(
                self.cr, self.uid,
                [('order_type_id.type', '=', 'P'), ('date', '=', self.date), ('asset_level1.id', '=', self.asset_line)],
                # order='asset_level1.code, asset_id.code', - por defecto ya está ordenado por código
                context=self.localcontext)
            orders = self.pool.get('sigma2.maintenance.order').read(
                self.cr, self.uid, order_ids, ['code', 'date', 'asset_id', 'description'],
                context=self.localcontext)
            res.append({'name': line['code'] + ' - ' + line['name'], 'code': preventive_code + line['code'],
                        'orders': orders})
        else:
            lines = self.pool.get('sigma2.asset').search(
                self.cr, self.uid,
                [('status', '=', 'active'), ('asset_type_id.type', '=', 'line')],
                # order='code', - por defecto ya está ordenado por código
                context=self.localcontext)
            for line_id in lines:
                line = self.pool.get('sigma2.asset').read(self.cr, self.uid, [line_id], ['code', 'name'],
                                                          context=self.localcontext)[0]
                order_ids = self.pool.get('sigma2.maintenance.order').search(
                    self.cr, self.uid,
                    [('order_type_id.type', '=', 'P'), ('date', '=', self.date), ('asset_level1.id', '=', line_id)],
                    # order='asset_level1.code, asset_id.code', - por defecto ya está ordenado por código
                    context=self.localcontext)
                if order_ids:
                    orders = self.pool.get('sigma2.maintenance.order').read(
                        self.cr, self.uid, order_ids, ['code', 'date', 'asset_id', 'description'],
                        context=self.localcontext)
                    res.append({'name': line['code'] + ' - ' + line['name'], 'code': preventive_code + line['code'],
                                'orders': orders})

        return res


class report_preventive_list(osv.AbstractModel):
    _name = 'report.sigma2.report_preventive_list'
    _inherit = 'report.abstract_report'
    _template = 'sigma2.report_preventive_list'
    _wrapped_report_class = preventive_list
