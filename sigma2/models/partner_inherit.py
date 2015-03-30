# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)

class res_partner(models.Model):
    _inherit = 'res.partner'
    _name = 'res.partner'

    contact = fields.Char('Contacto')
