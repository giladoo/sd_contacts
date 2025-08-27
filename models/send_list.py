from odoo import models, fields, api

class SdContactsSendList(models.Model):
    _name = "sd_contacts.send_list"
    _description = "Send List"

    location = fields.Many2one('hr.work.location', required=True)
    employee_id = fields.Many2many('hr.employee', required=True)
