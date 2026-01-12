import logging
from datetime import datetime

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AccountDeductionLine(models.Model):
    _name = 'account.deduction.line'
    _description = 'account.deduction.line'

    deduction_id =fields.Many2one('account.move', required=True, ondelete="restrict")
    invoice_to_deduct = fields.Many2one('account.move', string="Document Ref")
    date_deduction = fields.Date("Date", default=datetime.now())
    amount_pending = fields.Float("Amount", default="invoice_to_deduct.amount_residual", readonly=True)
    amount_to_deduct = fields.Float("Deduction/Payment", default=0.0)
    description = fields.Char("Description", default="")
    is_settled = fields.Boolean(default=False, readonly=True)

    @api.depends('invoice_to_deduct')
    @api.onchange("invoice_to_deduct")
    def _compute_amount_pending(self):
        '''Calculate amount pending'''
        for record in self:
            record.amount_pending = record.invoice_to_deduct.amount_residual

    @api.depends("invoice_to_deduct")
    @api.onchange("invoice_to_deduct")
    def _get_description(self):
        '''Return invoice description'''
        desc = ""

        for record in self:
            for line in record.invoice_to_deduct.invoice_line_ids:
                desc = "".join(str(line.name)) + "/"
        record.description = desc   
