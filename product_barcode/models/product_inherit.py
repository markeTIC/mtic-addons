# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import SUPERUSER_ID
from openerp import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class product_template(models.Model):
    _inherit = "product.template"

    barcode = fields.Char('Código de barras', related='product_variant_ids.barcode')


class product_product(models.Model):
    _inherit = 'product.product'

    barcode = fields.Char('Código de barras', required=False, select=True)

