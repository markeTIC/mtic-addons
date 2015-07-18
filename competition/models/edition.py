# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from datetime import timedelta

import pytz

from openerp import models, fields, api, _
from openerp.exceptions import Warning

import logging

_logger = logging.getLogger(__name__)

class CompetitionEdition(models.Model):
    """Competition Edition"""
    _name = 'competition.edition'
    _description = 'Edicion de competicion'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'date_begin'

    name = fields.Char(string='Nombre', translate=True, required=True)
    competition_id = fields.Many2one(
        'competition.competition', string='Competición', readonly=True, required=True, ondelete='cascade',
        states={'draft': [('readonly', False)]})
    type = fields.Many2one(
        'competition.type', string='Tipo de competición', readonly=True, states={'draft': [('readonly', False)]})
    registration_type = fields.Selection(
        selection=[
            ('individual', 'Individual'),
            ('team', 'Equipos'),
        ],
        string='Tipo de registro', default='team', required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('confirm', 'Confirmada'),
            ('done', 'Realizada'),
            ('cancel', 'Cancelada')
        ], string='Estado', default='draft', readonly=True, required=True, copy=False,
        help="Si se crea la edición de la competición el estado es 'Borrador'. Si se confirma la realización de la edición en las fechas indicadas se establece a 'Confirmada'. Si la edición ha pasado, el estado se establece a 'Realizada'. Si se cancela la edición se establece el estado a 'Cancelada', no se visualizará en la web.")
    description = fields.Html(
        string='Descripción', translate=True,
        readonly=False, states={'done': [('readonly', True)]})
    address_id = fields.Many2one(
        'res.partner', string='Ubicación', default=lambda self: self.env.user.company_id.partner_id,
        readonly=False, states={'done': [('readonly', True)]})
    organizer_id = fields.Many2one(
        'res.partner', string='Organizador',
        default=lambda self: self.env.user.company_id.partner_id)

    reply_to = fields.Char(
        string='Dirección responder a',
        readonly=False, states={'done': [('readonly', True)]})
    email_competition_id = fields.Many2one(
        'email.template', string='Mensaje confirmación competición',
        domain=[('model', '=', 'competition.registration')])
    email_registration_id = fields.Many2one(
        'email.template', string='Mensaje notificación registro',
        domain=[('model', '=', 'competition.registration')])
    email_confirmation_id = fields.Many2one(
        'email.template', string='Mensaje confirmación registro',
        domain=[('model', '=', 'competition.registration')])

    seats_max = fields.Integer(
        string='Plazas disponibles', readonly=True, states={'draft': [('readonly', False)]})
    seats_min = fields.Integer(
        string='Plazas mínimas a cubrir', readonly=True, states={'draft': [('readonly', False)]})

    seats_reserved = fields.Integer(
        string='Plazas reservadas', store=True, readonly=True, compute='_compute_seats')
    seats_available = fields.Integer(
        string='Plazas disponibles', store=True, readonly=True, compute='_compute_seats')
    seats_unconfirmed = fields.Integer(
        string='Plazas reservadas sin confirmar', store=True, readonly=True, compute='_compute_seats')
    seats_used = fields.Integer(
        string='Número de participantes', store=True, readonly=True, compute='_compute_seats')
    registration_ids = fields.One2many(
        'competition.registration', 'edition_id', string='Registros',
        readonly=False, states={'done': [('readonly', True)]})
    count_registrations = fields.Integer(
        string='Número de registros', compute='_count_registrations')
    company_id = fields.Many2one('res.company', string='Empresa', related='competition_id.company_id',
                                 store=True, readonly=True, states={'draft': [('readonly', False)]})
    is_subscribed = fields.Boolean(string='Suscrito', compute='_compute_subscribe')
    date_begin = fields.Datetime(
        string='Fecha inicio', required=True, readonly=True, states={'draft': [('readonly', False)]})
    date_end = fields.Datetime(
        string='Fecha fin', required=True, readonly=True, states={'draft': [('readonly', False)]})
    date_tz = fields.Selection(
        '_tz_get', string='Zona horaria', default=lambda self: self._context.get('tz', 'UTC'))
    date_begin_located = fields.Datetime(string='Fecha inicio local', compute='_compute_date_begin_tz')
    date_end_located = fields.Datetime(string='Fecha fin local', compute='_compute_date_end_tz')
    user_id = fields.Many2one('res.users', string='Usuario', states={'done': [('readonly', True)]})

    active = fields.Boolean('Activo')

    _defaults = {
        'active': True,
    }

    @api.multi
    @api.depends('seats_max', 'registration_ids.state', 'registration_ids.nb_register')
    def _compute_seats(self):
        """ Determine reserved, available, reserved but unconfirmed and used seats. """
        # initialize fields to 0
        for edition in self:
            edition.seats_unconfirmed = edition.seats_reserved = edition.seats_used = 0
        # aggregate registrations by event and by state
        if self.ids:
            state_field = {
                'draft': 'seats_unconfirmed',
                'open': 'seats_reserved',
                'done': 'seats_used',
            }
            query = """ SELECT edition_id, state, sum(nb_register)
                        FROM competition_registration
                        WHERE edition_id IN %s AND state IN ('draft', 'open', 'done')
                        GROUP BY edition_id, state
                    """
            self._cr.execute(query, (tuple(self.ids),))
            for edition_id, state, num in self._cr.fetchall():
                edition = self.browse(edition_id)
                edition[state_field[state]] += num
        # compute seats_available
        for edition in self:
            edition.seats_available = \
                edition.seats_max - (edition.seats_reserved + edition.seats_used) \
                if edition.seats_max > 0 else 0

    @api.one
    @api.depends('registration_ids')
    def _count_registrations(self):
        self.count_registrations = len(self.registration_ids)

    @api.model
    def _tz_get(self):
        return [(x, x) for x in pytz.all_timezones]

    @api.one
    @api.depends('date_tz', 'date_begin')
    def _compute_date_begin_tz(self):
        if self.date_begin:
            self_in_tz = self.with_context(tz=(self.date_tz or 'UTC'))
            date_begin = fields.Datetime.from_string(self.date_begin)
            self.date_begin_located = fields.Datetime.to_string(fields.Datetime.context_timestamp(self_in_tz, date_begin))
        else:
            self.date_begin_located = False

    @api.one
    @api.depends('date_tz', 'date_end')
    def _compute_date_end_tz(self):
        if self.date_end:
            self_in_tz = self.with_context(tz=(self.date_tz or 'UTC'))
            date_end = fields.Datetime.from_string(self.date_end)
            self.date_end_located = fields.Datetime.to_string(fields.Datetime.context_timestamp(self_in_tz, date_end))
        else:
            self.date_end_located = False

    @api.one
    @api.depends('registration_ids.user_id', 'registration_ids.state')
    def _compute_subscribe(self):
        """ Determine whether the current user is already subscribed to any event in `self` """
        user = self.env.user
        self.is_subscribed = any(
            reg.user_id == user and reg.state in ('open', 'done')
            for reg in self.registration_ids
        )

    @api.multi
    @api.depends('name', 'date_begin', 'date_end')
    def name_get(self):
        result = []
        for edition in self:
            dates = [dt.split(' ')[0] for dt in [edition.date_begin, edition.date_end] if dt]
            dates = sorted(set(dates))
            result.append((edition.id, '%s (%s)' % (edition.name, ' - '.join(dates))))
        return result

    @api.one
    @api.constrains('seats_max', 'seats_available')
    def _check_seats_limit(self):
        if self.seats_max and self.seats_available < 0:
            raise Warning(_('No hay plazas disponibles.'))

    @api.one
    @api.constrains('date_begin', 'date_end')
    def _check_closing_date(self):
        if self.date_end < self.date_begin:
            raise Warning(_('La fecha de fin no puede ser anterior a la fecha de inicio.'))

    @api.one
    def button_draft(self):
        self.state = 'draft'

    @api.one
    def button_cancel(self):
        for edition_reg in self.registration_ids:
            if edition_reg.state == 'done':
                raise Warning(_("Ya hay un registro de esta edición en estado 'Realizada'. Debe cambiarse a borrador para poder cancelar esta edición."))
        self.registration_ids.write({'state': 'cancel'})
        self.state = 'cancel'

    @api.one
    def button_done(self):
        self.state = 'done'

    @api.one
    def confirm_competition_edition(self):
        if self.email_confirmation_id:
            # send reminder that will confirm the event for all the people that were already confirmed
            regs = self.registration_ids.filtered(lambda reg: reg.state not in ('draft', 'cancel'))
            regs.mail_user_confirm()
        self.state = 'confirm'

    @api.one
    def button_confirm(self):
        """ Confirm competition edition and send confirmation email to all register peoples """
        self.confirm_competition_edition()

    @api.one
    def subscribe_to_competition_edition(self):
        """ Subscribe the current user to a given competition edition """
        user = self.env.user
        num_of_seats = int(self._context.get('ticket', 1))
        regs = self.registration_ids.filtered(lambda reg: reg.user_id == user)
        # the subscription is done as SUPERUSER_ID because in case we share the
        # kanban view, we want anyone to be able to subscribe
        if not regs:
            regs = regs.sudo().create({
                'competition_edition_id': self.id,
                'email': user.email,
                'name': user.name,
                'user_id': user.id,
                'nb_register': num_of_seats,
            })
        else:
            regs.write({'nb_register': num_of_seats})
        regs.sudo().confirm_registration()

    @api.one
    def unsubscribe_to_competition_edition(self):
        """ Unsubscribe the current user from a given competition edition """
        # the unsubscription is done as SUPERUSER_ID because in case we share
        # the kanban view, we want anyone to be able to unsubscribe
        user = self.env.user
        regs = self.sudo().registration_ids.filtered(lambda reg: reg.user_id == user)
        regs.button_reg_cancel()

    @api.onchange('competition_id')
    def _onchange_type(self):
        if self.competition_id:
            self.reply_to = self.competition_id.default_reply_to
            self.email_competition_id = self.competition_id.default_email_competition
            self.email_registration_id = self.competition_id.default_email_registration
            self.seats_min = self.competition_id.default_seats_min
            self.seats_max = self.competition_id.default_seats_max
            self.type = self.competition_id.type
            self.organizer_id = self.competition_id.organizer_id

    @api.onchange('date_begin')
    def _onchange_date_begin(self):
        if self.date_begin and not self.date_end:
            date_begin = fields.Datetime.from_string(self.date_begin)
            self.date_end = fields.Datetime.to_string(date_begin + timedelta(hours=1))


