'''Class to compute multiple orders selected from the fuel order tree'''

from odoo import models

class carrierOrderConfirm(models.TransientModel):
    _name = 'fuel.voucher.confirm'
    _description = "Wizard - Fuel Order Confirm/Cancel"

    def fuel_confirm(self):
        """filter the records of the state 'draft' and 'sent', and will confirm this and others will be skipped"""
        
        quotations = self._context.get('active_ids')
        
        quotations_ids = self.env['fuel.voucher'].browse(quotations).\
            filtered(lambda x: x.status != 'posted')

        for quotation in quotations_ids:
            quotation.action_post()
