# -*- coding: utf-8 -*-
################################################################
#    License, author and contributors information in:          #
#    __openerp__.py file at the root folder of this module.    #
################################################################

from openerp import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)

class CompetitionType(models.Model):
    """ Competition Type """
    _name = 'competition.type'
    _description = 'Tipo de competicion'

    name = fields.Char(string='Tipo de competición', required=True, select=True)
    parent_id = fields.Many2one('competition.type', 'Padre', select=True, ondelete='restrict')
    notes = fields.Text('Notas')
    active = fields.Boolean('Activo')

    _defaults = {
        'active': True,
    }

    _order = 'name'

    _sql_constraints = [
        ('name_uniq', 'unique(name)', _("No puede crear más de un tipo con el mismo nombre."))
    ]
