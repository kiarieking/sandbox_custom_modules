# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class ProductTemplate(models.Model):
    _inherit='product.template'

    partner_id = fields.Many2one('res.partner', string="Related Customer",readonly=False)
    is_active = fields.Boolean(string="Product Is Active", default=True)
    is_inventory = fields.Boolean(string="Inventory Product", default=False)
    core_product_id = fields.Char(string="Core Product ID")
    core_shipper_id = fields.Char(string="Shipper ID")
    loading_charge = fields.Float("Loading Charge", default=0.0)
