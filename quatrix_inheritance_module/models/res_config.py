from odoo import models, fields


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