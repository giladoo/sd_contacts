from odoo import models, fields, api

class SdContactsGates(models.Model):
    _name = "sd_contacts.gate_info"
    _description = "Gate Information"

    name = fields.Char(required=True)
    code = fields.Char(required=True, help="ex: G1, G2, ...")
    location = fields.Many2one('hr.work.location', required=True)
