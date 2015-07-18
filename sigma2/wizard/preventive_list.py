# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp.osv import fields, osv

class sigma2_preventive_list(osv.osv_memory):
    _name = 'sigma2.preventive_list'
    _description = 'Preventive List'

    _columns = {
        'date': fields.date('Fecha', required=True),
        'asset_line': fields.many2one('sigma2.asset', 'Línea',
                                      domain="[('status', '=', 'active'), ('asset_type_id.type', '=', 'line'), ]"),
    }
    _defaults = {
        'date': fields.date.today(),
    }

    def print_report(self, cr, uid, ids, context=None):
        """
        To get the date and print the report
        @return : return report
        """
        if context is None:
            context = {}
        datas = {'ids': context.get('active_ids', [])}
        res = self.read(cr, uid, ids, ['date', 'asset_line'], context=context)
        res = res and res[0] or {}
        res['asset_line'] = res['asset_line'] and res['asset_line'][0]
        datas['form'] = res
        return self.pool['report'].get_action(cr, uid, [], 'sigma2.report_preventive_list', data=datas, context=context)
