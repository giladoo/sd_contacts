from odoo import models, fields, api


class SdContactsEmergencyEmails(models.Model):
    _inherit = "hr.work.location"

    emergency_emails = fields.Many2many('hr.employee')