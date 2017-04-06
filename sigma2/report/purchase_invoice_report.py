# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp.osv import fields,osv
from openerp import tools

class purchase_invoice_report(osv.osv):
    _name = "sigma2.purchase_invoice_report"
    _description = "Facturas de compra"
    _auto = False
    _columns = {
        'date': fields.datetime('Fecha', readonly=True, help="Fecha de emisión de la factura"),
        'date_year': fields.char('Año', readonly=True, length=5),
        'date_month': fields.char('Mes', readonly=True, length=2),
        'product_id': fields.many2one('product.product', 'Producto', readonly=True),
        'partner_id':fields.many2one('res.partner', 'Proveedor', readonly=True),
        'company_id':fields.many2one('res.company', 'Empresa', readonly=True),
        'user_id':fields.many2one('res.users', 'Usuario', readonly=True),
        'quantity': fields.integer('Cantidad', readonly=True),
        'price_total': fields.float('Importe', readonly=True),
        'nbr': fields.integer('Núm. de líneas', readonly=True),
        'category_id': fields.many2one('product.category', 'Familia', readonly=True),
        'cost_area_id': fields.many2one('sigma2.cost.area', 'Área de coste', readonly=True),
        'cost_group_id': fields.many2one('sigma2.cost.area', 'Grupo de gasto', readonly=True),
        'investment_id': fields.many2one('sigma2.investment', 'Inversión', readonly=True),
        'asset_id': fields.many2one('sigma2.asset', 'Zona de fábrica', readonly=True)
    }
    _order = 'date desc'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'sigma2_purchase_invoice_report')
        cr.execute("""
            create or replace view sigma2_purchase_invoice_report as (
                select
                    min(l.id) as id,
                    i.date_value as date,
                    to_char(i.date_value, 'YYYY') as date_year,
                    to_char(i.date_value, 'MM') as date_month,
                    i.partner_id as partner_id,
                    i.create_uid as user_id,
                    i.company_id as company_id,
                    l.product_id,
                    t.categ_id as category_id,
                    l.cost_area_id,
                    c.parent_id as cost_group_id,
                    l.investment_id,
                    l.asset_id,
                    sum(l.quantity) as quantity,
                    count(*) as nbr,
                    sum(l.price_subtotal) as price_total
                from account_invoice_line l
                    join account_invoice i on (l.invoice_id=i.id)
                        left join product_product p on (l.product_id=p.id)
                        left join product_template t on (p.product_tmpl_id=t.id)
                        left join sigma2_cost_area c on (l.cost_area_id=c.id)
                group by
                    i.date_value,
                    i.date_invoice,
                    i.create_uid,
                    i.company_id,
                    i.partner_id,
                    l.product_id,
                    t.categ_id,
                    l.cost_area_id,
                    c.parent_id,
                    l.investment_id,
                    l.asset_id
                order by id
            )
        """)
