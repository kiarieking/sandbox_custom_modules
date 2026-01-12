from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class ResUsers(models.Model):
    _inherit = 'res.partner'

    carrier_carrier_id = fields.Char(string="Carrier ID", readonly=False)
    core_shipper_id = fields.Char("Shipper ID")
    is_partner_vatable = fields.Boolean(string="Partner Vatable")
    is_customer = fields.Boolean("is Shipper")
    is_vendor = fields.Boolean("Is Vendor", default=True)
    require_certificate_number = fields.Boolean(string="Require Certificate Number On Invoices")

    _sql_constraints = [
                ('carrier_carrier_id_unique', 
                'unique(carrier_carrier_id)',
                'Enter another value - Carrier ID has to be unique!')
    ]