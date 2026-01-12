from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    hscode_id = fields.Many2one('product.hscode', string='KRA Hs Code',
                                help='Kra approved code for tax exempt products')


class ProductHsCodes(models.Model):
    _name = 'product.hscode'
    _description = 'Product HsCodes'

    name = fields.Char(string='HsCode', required=True)
    hsdesc = fields.Char(string='HsDesc', required=True)
    tax_id = fields.Many2one('account.tax', string='Tax', required=True)
    description = fields.Text(string='Description')
    active = fields.Boolean(string='Active', default=True)
