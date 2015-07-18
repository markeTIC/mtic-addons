# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

import babel.dates
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import werkzeug.urls
from werkzeug.exceptions import NotFound

from openerp import http
from openerp import tools
from openerp.http import request
from openerp.tools.translate import _
from openerp.addons.website.models.website import slug


class CompetitionWebsite(http.Controller):
    @http.route(['/edition', '/edition/page/<int:page>'], type='http', auth="public", website=True)
    def editions(self, page=1, **searches):
        cr, uid, context = request.cr, request.uid, request.context
        edition_obj = request.registry['competition.edition']
        type_obj = request.registry['competition.type']

        searches.setdefault('date', 'all')
        searches.setdefault('type', 'all')

        domain_search = {}

        def sdn(date):
            return date.strftime('%Y-%m-%d 23:59:59')

        def sd(date):
            return date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)

        today = datetime.today()
        dates = [
            ['all', _('Próximas'), [("date_end", ">", sd(today))], 0],
            ['today', _('Hoy'), [
                ("date_end", ">", sd(today)),
                ("date_begin", "<", sdn(today))],
                0],
            ['week', _('Esta semana'), [
                ("date_end", ">=", sd(today + relativedelta(days=-today.weekday()))),
                ("date_begin", "<", sdn(today + relativedelta(days=6-today.weekday())))],
                0],
            ['nextweek', _('Próxima semana'), [
                ("date_end", ">=", sd(today + relativedelta(days=7-today.weekday()))),
                ("date_begin", "<", sdn(today + relativedelta(days=13-today.weekday())))],
                0],
            ['month', _('Este mes'), [
                ("date_end", ">=", sd(today.replace(day=1))),
                ("date_begin", "<", (today.replace(day=1) + relativedelta(months=1)).strftime('%Y-%m-%d 00:00:00'))],
                0],
            ['nextmonth', _('Próximo mes'), [
                ("date_end", ">=", sd(today.replace(day=1) + relativedelta(months=1))),
                ("date_begin", "<", (today.replace(day=1)  + relativedelta(months=2)).strftime('%Y-%m-%d 00:00:00'))],
                0],
            ['old', _('Pasadas'), [
                ("date_end", "<", today.strftime('%Y-%m-%d 00:00:00'))],
                0],
        ]

        # search domains
        current_date = None
        current_type = None
        for date in dates:
            if searches["date"] == date[0]:
                domain_search["date"] = date[2]
                if date[0] != 'all':
                    current_date = date[1]
        if searches["type"] != 'all':
            current_type = type_obj.browse(cr, uid, int(searches['type']), context=context)
            domain_search["type"] = [("type", "=", int(searches["type"]))]

        def dom_without(without):
            domain = [('state', "in", ['draft', 'confirm', 'done'])]
            for key, search in domain_search.items():
                if key != without:
                    domain += search
            return domain

        # count by domains without self search
        for date in dates:
            if date[0] != 'old':
                date[3] = edition_obj.search(
                    request.cr, request.uid, dom_without('date') + date[2],
                    count=True, context=request.context)

        domain = dom_without('type')
        types = edition_obj.read_group(
            request.cr, request.uid, domain, ["id", "type"], groupby="type",
            orderby="type", context=request.context)
        type_count = edition_obj.search(request.cr, request.uid, domain,
                                        count=True, context=request.context)
        types.insert(0, {
            'type_count': type_count,
            'type': ("all", _("Todas las categorías"))
        })

        step = 10  # Number of editions per page
        count = edition_obj.search(
            request.cr, request.uid, dom_without("none"), count=True,
            context=request.context)
        pager = request.website.pager(
            url="/edition",
            url_args={'date': searches.get('date'), 'type': searches.get('type')},
            total=count,
            page=page,
            step=step,
            scope=5)

        order = 'website_published desc, date_begin'
        if searches.get('date', 'all') == 'old':
            order = 'website_published desc, date_begin desc'
        obj_ids = edition_obj.search(
            request.cr, request.uid, dom_without("none"), limit=step,
            offset=pager['offset'], order=order, context=request.context)
        editions_ids = edition_obj.browse(request.cr, request.uid, obj_ids,
                                        context=request.context)

        values = {
            'current_date': current_date,
            'current_type': current_type,
            'edition_ids': editions_ids,
            'dates': dates,
            'types': types,
            'pager': pager,
            'searches': searches,
            'search_path': "?%s" % werkzeug.url_encode(searches),
        }

        return request.website.render("competition_website.index", values)

    @http.route(['/edition/<model("competition.edition"):edition>/page/<path:page>'], type='http', auth="public", website=True)
    def edition_page(self, edition, page, **post):
        values = {
            'edition': edition,
            'main_object': edition
        }

        if '.' not in page:
            page = 'competition_website.%s' % page

        try:
            request.website.get_template(page)
        except ValueError, e:
            # page not found
            raise NotFound

        return request.website.render(page, values)

    @http.route(['/edition/<model("competition.edition"):edition>'], type='http', auth="public", website=True)
    def edition(self, edition, **post):
        if edition.menu_id and edition.menu_id.child_id:
            target_url = edition.menu_id.child_id[0].url
        else:
            target_url = '/edition/%s/register' % str(edition.id)
        if post.get('enable_editor') == '1':
            target_url += '?enable_editor=1'
        return request.redirect(target_url)

    @http.route(['/edition/<model("competition.edition"):edition>/register'], type='http', auth="public", website=True)
    def edition_register(self, edition, **post):
        values = {
            'edition': edition,
            'main_object': edition,
            'range': range,
        }
        return request.website.render("competition_website.edition_description_full", values)

    @http.route('/edition/add_edition', type='http', auth="user", methods=['POST'], website=True)
    def add_edition(self, edition_name="Nueva edición", **kwargs):
        return self._add_edition(edition_name, request.context, **kwargs)

    def _add_edition(self, edition_name=None, context={}, **kwargs):
        if not edition_name:
            edition_name = _("Nueva edición")
        edition_rs = request.registry.get('competition.edition')
        date_begin = datetime.today() + timedelta(days=14)
        vals = {
            'name': edition_name,
            'date_begin': date_begin.strftime('%Y-%m-%d'),
            'date_end': (date_begin + timedelta(days=1)).strftime('%Y-%m-%d'),
        }
        edition_id = edition_rs.create(request.cr, request.uid, vals, context=context)
        edition = edition_rs.browse(request.cr, request.uid, edition_id, context=context)
        return request.redirect("/edition/%s/register?enable_editor=1" % slug(edition))

    def get_formated_date(self, edition):
        context = request.context
        start_date = datetime.strptime(edition.date_begin, tools.DEFAULT_SERVER_DATETIME_FORMAT).date()
        end_date = datetime.strptime(edition.date_end, tools.DEFAULT_SERVER_DATETIME_FORMAT).date()
        month = babel.dates.get_month_names('abbreviated', locale=context.get('lang', 'en_US'))[start_date.month]
        return _('%(month)s %(start_day)s%(end_day)s') % {
            'month': month,
            'start_day': start_date.strftime("%e"),
            'end_day': (end_date != start_date and ("-"+end_date.strftime("%e")) or "")
        }
