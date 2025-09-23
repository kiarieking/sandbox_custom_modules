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


class ResConfigSettings(models.TransientModel):
    _inherit = ['res.config.settings']

    payment_installment_id = fields.Char(string='Payment Installment %', default=15)
    payment_full_id = fields.Char(string='Payment Full%', default=100)

    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
    
        res.update(
            payment_installment_id = self.env['ir.config_parameter'].sudo().get_param('quatrix_inheritance_module.payment_installment_id'),
            payment_full_id = self.env['ir.config_parameter'].sudo().get_param('quatrix_inheritance_module.payment_full_id'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        payment_installment_percentage = self.payment_installment_id and self.payment_installment_id or False
        payment_full_percentage = self.payment_full_id and self.payment_full_id or False

        param.set_param('quatrix_inheritance_module.payment_installment_id', payment_installment_percentage)
        param.set_param('quatrix_inheritance_module.payment_full_id', payment_full_percentage)