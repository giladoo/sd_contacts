# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
import json
class ResUsersSdContacts(models.Model):
    _inherit = 'res.users'

    sd_contacts_companies = fields.Many2many('res.company', )

