from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    order_no = fields.Char(string="Order No")
    date = fields.Date(readonly=False, required=True, string="Date")
    
    @api.model
    def _prepare_account_move_line(self, move=False):
        res = super(PurchaseOrderLine, self)._prepare_account_move_line(move)

        for record in self:
            res['additional_charges'] = 0.0
            res['order_no'] = record.order_no
            res['dates'] = record.date

        return res