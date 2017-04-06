# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import SUPERUSER_ID
from openerp import models, fields, api, _
from openerp.osv import expression

import logging

_logger = logging.getLogger(__name__)


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    cost_area_id = fields.Many2one('sigma2.cost.area', 'Área de coste', required=True, ondelete='restrict',
                                   readonly=False, states={'done': [('readonly', True)]})
    is_investment = fields.Boolean('Inversión', compute='_compute_is_investment', store=False)
    investment_id = fields.Many2one('sigma2.investment', 'Inversión', required=False, ondelete='restrict',
                                    readonly=False, states={'done': [('readonly', True)]})
    asset_id = fields.Many2one('sigma2.asset', 'Zona de fábrica', domain="[('status', '=', 'active'), ('asset_type_id.type', '=', 'line'), ]",
                               required=False, ondelete='restrict', readonly=False, states={'done': [('readonly', True)]})

    @api.one
    @api.depends('cost_area_id')
    def _compute_is_investment(self):
        if self.cost_area_id:
            self.is_investment = self.cost_area_id.investment
        else:
            self.is_investment = False
        if not self.is_investment:
            self.investment_id = None

    @api.v7
    def _prepare_inv_line(self, cr, uid, account_id, order_line, context=None):
        res = super(purchase_order, self)._prepare_inv_line(cr, uid, account_id, order_line, context)
        res['cost_area_id'] = order_line.cost_area_id and order_line.cost_area_id.id or False
        res['investment_id'] = order_line.investment_id and order_line.investment_id.id or False
        res['asset_id'] = order_line.asset_id and order_line.asset_id.id or False

        return res


class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    cost_area_id = fields.Many2one('sigma2.cost.area', 'Área de coste', required=True, ondelete='restrict',
                                   readonly=False, states={'done': [('readonly', True)]})
    is_investment = fields.Boolean('Inversión', compute='_compute_is_investment', store=False)
    investment_id = fields.Many2one('sigma2.investment', 'Inversión', required=False, ondelete='restrict',
                                    readonly=False, states={'done': [('readonly', True)]})
    asset_id = fields.Many2one('sigma2.asset', 'Zona de fábrica', domain="[('status', '=', 'active'), ('asset_type_id.type', '=', 'line'), ]",
                               required=False, ondelete='restrict', readonly=False, states={'done': [('readonly', True)]})

    @api.one
    @api.depends('cost_area_id')
    def _compute_is_investment(self):
        if self.cost_area_id:
            self.is_investment = self.cost_area_id.investment
        else:
            self.is_investment = False
        if not self.is_investment:
            self.investment_id = None


class account_invoice(models.Model):
    _inherit = 'account.invoice'
    date_value = fields.Date('Fecha valor')

    @api.multi
    def _get_default_date_value(self, cr, uid, context=None):
        self.date_value = self.date_invoice

#    _defaults = {
#        'date_value': lambda self, cr, uid, c=None: self._get_default_date_value(cr, uid, context=c)
#    }

    @api.multi
    def onchange_payment_term_date_invoice(self, payment_term_id, date_invoice):
        res = super(account_invoice, self).onchange_payment_term_date_invoice(payment_term_id, date_invoice)
        if not self.date_value or self.date_value == self.date_invoice:
            res['value']['date_value'] = res['value']['date_due']
        return res

    @api.multi
    def onchange_supplier_invoice_number(self, date_invoice):
        if not self.date_value:
            return {'value': {'date_value': date_invoice}}
        return {}


class account_invoice_line(models.Model):
    """ Override account_invoice_line to add the cost area and investment id"""
    _inherit = 'account.invoice.line'
    cost_area_id = fields.Many2one('sigma2.cost.area', 'Área de coste', required=False, ondelete='restrict')
    is_investment = fields.Boolean('Inversión', compute='_compute_is_investment', store=False)
    investment_id = fields.Many2one('sigma2.investment', 'Inversión', required=False, ondelete='restrict')
    asset_id = fields.Many2one('sigma2.asset', 'Zona de fábrica', domain="[('status', '=', 'active'), ('asset_type_id.type', '=', 'line'), ]",
                               required=False, ondelete='restrict')

    @api.one
    @api.depends('cost_area_id')
    def _compute_is_investment(self):
        if self.cost_area_id:
            self.is_investment = self.cost_area_id.investment
        else:
            self.is_investment = False
        if not self.is_investment:
            self.investment_id = None


