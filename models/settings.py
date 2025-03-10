# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


# #################################################################################################
class SdContactsSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    show_job_title = fields.Boolean(config_parameter='sd_contacts.show_job_title',)
    show_projects = fields.Boolean(config_parameter='sd_contacts.show_projects',)
    show_locations = fields.Boolean(config_parameter='sd_contacts.show_locations', )
