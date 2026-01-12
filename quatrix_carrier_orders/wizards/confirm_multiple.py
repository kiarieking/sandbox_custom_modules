from odoo import models
class carrierOrderConfirm(models.TransientModel):
    _name = 'carrier.order.confirm'
    _description = "Wizard - Carrier Order Confirm/Cancel"

    def carrier_confirm(self):
        """filter the records of the state 'draft' and 'sent', and will confirm this and others will be skipped"""
        quotations = self._context.get('active_ids')
        
        #here in quotations you will get the id of the selected records
        
        quotations_ids = self.env['carrier.order'].browse(quotations).\
            filtered(lambda x: x.status != 'posted')

        for quotation in quotations_ids:
            quotation.action_post()