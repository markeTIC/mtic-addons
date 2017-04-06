# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp.osv import fields, osv


class sigma2_create_product_labels(osv.osv_memory):
    _name = 'sigma2.create_product_labels'
    _description = 'Create product labels'

    def create_product_labels(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        label_obj = self.pool.get('sigma2.product_label')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        new_labels = []
        if context is None:
            context = {}
        for product in product_obj.browse(cr, uid, context.get(('active_ids'), []), context=context):
            label_data = {
                'name': product.name,
                'code': product.default_code,
                'barcode': product.barcode,
            }
            if product.label_by_unit:
                i = 0
                num = product.qty_available
                if num == 0:
                    num = 1
                while i < num:
                    label_id = label_obj.create(cr, uid, label_data, context=context)
                    new_labels.append(label_id)
                    i = i + 1
            else:
                label_id = label_obj.create(cr, uid, label_data, context=context)
                new_labels.append(label_id)

        result = mod_obj.get_object_reference(cr, uid, 'sigma2', 'product_label_list_action')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['domain'] = "[('id','in', [" + ','.join(map(str, new_labels)) + "])]"

        return result
