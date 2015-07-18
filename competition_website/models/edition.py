# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp.osv import osv, fields
from openerp import SUPERUSER_ID

from openerp.tools.translate import _
import re

from openerp.addons.website.models.website import slug

class CompetitionEdition(osv.osv):
    _name = 'competition.edition'
    _inherit = ['competition.edition', 'website.seo.metadata']
    _track = {
        'website_published': {
            'competition_website.mt_edition_published': lambda self, cr, uid, obj, ctx=None: obj.website_published,
            'competition_website.mt_edition_unpublished': lambda self, cr, uid, obj, ctx=None: not obj.website_published
        },
    }

    def _get_new_menu_pages(self, cr, uid, edition, context=None):
        context = context or {}
        todo = [
            (_('Introducción'), 'competition_website.template_intro'),
            (_('Ubicación'), 'competition_website.template_location')
        ]
        web = self.pool.get('website')
        result = []
        for name, path in todo:
            name2 = name + ' ' + edition.name
            newpath = web.new_page(cr, uid, name2, path, ispage=False, context=context)
            url = "/edition/" + slug(edition) + "/page/" + newpath
            result.append((name, url))
        return result

    def _set_show_menu(self, cr, uid, ids, name, value, arg, context=None):
        menuobj = self.pool.get('website.menu')
        editionobj = self.pool.get('competition.edition')
        for edition in self.browse(cr, uid, [ids], context=context):
            if edition.menu_id and not value:
                menuobj.unlink(cr, uid, [edition.menu_id.id], context=context)
            elif value and not edition.menu_id:
                root = menuobj.create(cr, uid, {
                    'name': edition.name
                }, context=context)
                tocreate = self._get_new_menu_pages(cr, uid, event, context)
                tocreate.append((_('Inscribirse'), '/edition/%s/register' % slug(edition)))
                sequence = 0
                for name,url in tocreate:
                    menuobj.create(cr, uid, {
                        'name': name,
                        'url': url,
                        'parent_id': root,
                        'sequence': sequence
                    }, context=context)
                    sequence += 1
                editionobj.write(cr, uid, [edition.id], {'menu_id': root}, context=context)
        return True

    def _get_show_menu(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, '')
        for edition in self.browse(cr, uid, ids, context=context):
            res[edition.id] = bool(edition.menu_id)
        return res

    def _website_url(self, cr, uid, ids, field_name, arg, context=None):
        res = dict.fromkeys(ids, '')
        for edition in self.browse(cr, uid, ids, context=context):
            res[edition.id] = "/edition/" + slug(edition)
        return res

    def _default_hashtag(self, cr, uid, context={}):
        name = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.name
        return re.sub("[- \\.\\(\\)\\@\\#\\&]+", "", name).lower()

    _columns = {
        'twitter_hashtag': fields.char('Twitter Hashtag'),
        'website_published': fields.boolean('Visible en la web', copy=False),
        # TDE TODO FIXME: when website_mail/mail_thread.py inheritance work -> this field won't be necessary
        'website_message_ids': fields.one2many(
            'mail.message', 'res_id',
            domain=lambda self: [
                '&', ('model', '=', self._name), ('type', '=', 'comment')
            ],
            string='Mensajes de la web',
            help="Historia de mensajes en la web",
        ),
        'website_url': fields.function(_website_url, string="URL web", type="char"),
        'show_menu': fields.function(_get_show_menu, fnct_inv=_set_show_menu, type='boolean', string='Menú dedicado',
            help="Crea los menús Introducción, Ubicación e Inscribirse en la página de la edición en la web."),
        'menu_id': fields.many2one('website.menu', 'Menú de la edición'),
    }
    _defaults = {
        'show_menu': False,
        'twitter_hashtag': _default_hashtag
    }

    def google_map_img(self, cr, uid, ids, zoom=8, width=298, height=298, context=None):
        edition = self.browse(cr, uid, ids[0], context=context)
        if edition.address_id:
            return self.browse(cr, SUPERUSER_ID, ids[0], context=context).address_id.google_map_img()
        return None

    def google_map_link(self, cr, uid, ids, zoom=8, context=None):
        edition = self.browse(cr, uid, ids[0], context=context)
        if edition.address_id:
            return self.browse(cr, SUPERUSER_ID, ids[0], context=context).address_id.google_map_link()
        return None

