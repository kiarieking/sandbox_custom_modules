from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    order_no = fields.Char(string="Delivery No")
    date = fields.Date(string="Date", store=True)
    notes = fields.Text(string="Lines")
    additional_charges = fields.Float(string="Charges", default=0.0)
