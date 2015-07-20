# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

import werkzeug
from openerp.osv import osv, fields


def urlplus(url, params):
    return werkzeug.Href(url)(params or None)


class PartnerCoords(osv.osv):
    _inherit = "res.partner"

    _columns = {
        'coord_latitude': fields.char('Latitud'),
        'coord_longitude': fields.char('Longitud'),
    }

    def google_map_img_coord(self, cr, uid, ids, zoom=8, width=298, height=298, context=None):
        partner = self.browse(cr, uid, ids[0], context=context)
        param_center = '%s, %s %s, %s' % (partner.street or '', partner.city or '', partner.zip or '', partner.country_id and partner.country_id.name_get()[0][1] or '')
        param_markers = ''
        if partner.coord_latitude and partner.coord_longitude:
            param_center = '%s,%s' % (partner.coord_latitude, partner.coord_longitude)
            param_markers = '%s,%s' % (partner.coord_latitude, partner.coord_longitude)
        params = {
            'center': param_center,
            'size': "%sx%s" % (height, width),
            'zoom': zoom,
            'sensor': 'false',
            'markers': param_markers,
        }
        return urlplus('//maps.googleapis.com/maps/api/staticmap', params)

    def google_map_link_coord(self, cr, uid, ids, zoom=8, context=None):
        partner = self.browse(cr, uid, ids[0], context=context)
        param_q = '%s,%s %s, %s' % (partner.street or '', partner.city  or '', partner.zip or '', partner.country_id and partner.country_id.name_get()[0][1] or '')
        if partner.coord_latitude and partner.coord_longitude:
            param_q = '%s,%s' % (partner.coord_latitude, partner.coord_longitude)
        params = {
            'q': param_q,
            'z': 10
        }
        return urlplus('https://maps.google.com/maps', params)

