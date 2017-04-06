# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    document_number = fields.Char('Núm. albarán')


class stock_move(models.Model):
    _inherit = 'stock.move'

    @api.v7
    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        res = super(stock_move, self)._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)

        if inv_type == 'in_invoice' and move.purchase_line_id:
            purchase_line = move.purchase_line_id
            res['cost_area_id'] = purchase_line.cost_area_id and purchase_line.cost_area_id.id or False
            res['investment_id'] = purchase_line.investment_id and purchase_line.investment_id.id or False
            res['asset_id'] = purchase_line.asset_id and purchase_line.asset_id.id or False
        elif inv_type == 'in_refund' and move.origin_returned_move_id.purchase_line_id:
            purchase_line = move.origin_returned_move_id.purchase_line_id
            res['cost_area_id'] = purchase_line.cost_area_id and purchase_line.cost_area_id.id or False
            res['investment_id'] = purchase_line.investment_id and purchase_line.investment_id.id or False
            res['asset_id'] = purchase_line.asset_id and purchase_line.asset_id.id or False
        return res

