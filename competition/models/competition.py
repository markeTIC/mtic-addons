# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)

class CompetitionCompetition(models.Model):
    """Competition"""
    _name = 'competition.competition'
    _description = 'Competicion'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'name'

    name = fields.Char(string='Nombre', translate=True, required=True, readonly=False, states={'closed': [('readonly', True)]})
    type = fields.Many2one('competition.type', string='Tipo de competición', readonly=False, states={'closed': [('readonly', True)]})
    description = fields.Html(string='Descripción', translate=True, readonly=False, states={'closed': [('readonly', True)]})
    organizer_id = fields.Many2one(
        'res.partner', string='Organizador',
        default=lambda self: self.env.user.company_id.partner_id)
    default_reply_to = fields.Char(string='Responder a por defecto',
        help="Dirección de correo del organizador que se asigna al campo 'responder a' de todos los mensajes enviados automáticamente al confirmar la competición o el registro.")
    default_email_competition = fields.Many2one('email.template', string='Mensaje de confirmación de competición')
    default_email_registration = fields.Many2one('email.template', string='Mensaje de confirmación de registro')
    default_seats_min = fields.Integer(string='Núm. plazas mínimo por defecto', default=0)
    default_seats_max = fields.Integer(string='Núm. plazas máximo por defecto', default=0)
    default_registration_type = fields.Selection(
        selection=[
            ('individual', 'Individual'),
            ('team', 'Team'),
        ],
        string='Tipo de registro por defecto', default='team', required=True,
        readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection(
        [
            ('draft', 'Borrador'),
            ('open', 'Abierta'),
            ('close', 'Cerrada'),
            ('cancel', 'Cancelada')
        ], string='Estado', default='draft', readonly=True, required=True, copy=False,
        help="Cuando se crea la competición el estado es 'Borrador'. Si la competición está activa el estado es 'Abierta', se pueden crear ediciones. Si la competición está cerrada, el estado es 'Cerrada' y no pueden crearse nuevas ediciones. Si la competición se cancela, se establece el estado a 'Cancelada', no se visualizará en la web.")
    edition_ids = fields.One2many(
        'competition.edition', 'competition_id', string='Ediciones',
        readonly=False, states={'close': [('readonly', True)], 'cancel': [('readonly', True)]})
    company_id = fields.Many2one(
        'res.company', string='Empresa', change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('competition.competition'),
        required=False, readonly=True, states={'draft': [('readonly', False)]})
    active = fields.Boolean('Activo')

    _defaults = {
        'active': True,
    }

    @api.one
    def button_draft(self):
        self.state = 'draft'

    @api.one
    def button_cancel(self):
        self.edition_ids.write({'state': 'cancel'})
        self.state = 'cancel'

    @api.one
    def button_close(self):
        self.state = 'close'

    @api.one
    def button_open(self):
        self.state = 'open'
