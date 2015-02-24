# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp.osv import fields, osv

class product_template(osv.osv):
    _inherit = "product.template"

    _columns = {
        'manufacturer_id': fields.many2one('manufacturer.manufacturer','Fabricante', required=False, change_default=True, help="Seleccione el fabricante del producto"),
    }
