# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)

class CompetitionRegistration(models.Model):
    _name = 'competition.registration'
    _description = 'Registro en edicion de competicion'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'name, create_date desc'

    name = fields.Char(string='Nombre', select=True)
    origin = fields.Char(string='Documento origen', readonly=True)
    nb_register = fields.Integer(string='Número de participantes', required=True, default=1,
                                 readonly=True, states={'draft': [('readonly', False)]})
    edition_id = fields.Many2one(
        'competition.edition', string='Edición de competición', required=True, ondelete='cascade',
        readonly=True, states={'draft': [('readonly', False)]})
    partner_id = fields.Many2one(
        'res.partner', string='Persona',
        states={'done': [('readonly', True)]})
    date_open = fields.Datetime(string='Fecha registro', readonly=True)
    date_closed = fields.Datetime(string='Fecha participación', readonly=True)
    reply_to = fields.Char(string='Email de respuesta', related='edition_id.reply_to', readonly=True)
    log_ids = fields.One2many('mail.message', 'res_id', string='Registro', domain=[('model', '=', _name)])
    edition_begin_date = fields.Datetime(string="Fecha inicio competición",
                                         related='edition_id.date_begin', readonly=True)
    edition_end_date = fields.Datetime(string="Fecha fin competición",
                                       related='edition_id.date_end', readonly=True)
    user_id = fields.Many2one('res.users', string='Usuario', states={'done': [('readonly', True)]})
    company_id = fields.Many2one('res.company', string='Empresa', related='edition_id.company_id',
                                 store=True, readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('open', 'Confirmada'),
            ('done', 'Realizada'),
            ('cancel', 'Cancelada')
        ], string='Status', default='draft', readonly=True, copy=False)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Teléfono')

    active = fields.Boolean('Activo')

    _defaults = {
        'active': True,
    }

    @api.one
    @api.constrains('edition_id', 'state', 'nb_register')
    def _check_seats_limit(self):
        if self.edition_id.seats_max and \
                self.edition_id.seats_available < (self.nb_register if self.state == 'draft' else 0):
            raise Warning(_('No hay plazas disponibles.'))

    @api.one
    def do_draft(self):
        self.state = 'draft'

    @api.one
    def confirm_registration(self):
        self.edition_id.message_post(
            body=_('Nuevo registro confirmado: %s.') % (self.name or ''),
            subtype="competition.mt_edition_registration")
        self.message_post(body=_('Registro a edición de competición confirmado.'))
        self.state = 'open'

    @api.one
    def registration_open(self):
        """ Open Registration """
        self.confirm_registration()
        self.mail_user()

    @api.one
    def button_reg_close(self):
        """ Close Registration """
        today = fields.Datetime.now()
        if self.edition_id.date_begin <= today:
            self.write({'state': 'done', 'date_closed': today})
        else:
            raise Warning(_("Debe esperar al inicio de la competición para realizar ésta acción."))

    @api.one
    def button_reg_cancel(self):
        self.state = 'cancel'

    @api.one
    def mail_user(self):
        """Send email to user with email_template when registration is done """
        if self.edition_id.state == 'confirm' and self.edition_id.email_confirmation_id:
            self.mail_user_confirm()
        else:
            template = self.edition_id.email_registration_id
            if template:
                mail_message = template.send_mail(self.id)

    @api.one
    def mail_user_confirm(self):
        """Send email to user when the competition edition is confirmed """
        template = self.edition_id.email_confirmation_id
        if template:
            mail_message = template.send_mail(self.id)

    @api.onchange('partner_id')
    def _onchange_partner(self):
        if self.partner_id:
            contact_id = self.partner_id.address_get().get('default', False)
            if contact_id:
                contact = self.env['res.partner'].browse(contact_id)
                self.name = contact.name
                self.email = contact.email
                self.phone = contact.phone
