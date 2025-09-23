from odoo import api, fields, models
from odoo.exceptions import ValidationError

INVOICE_MAP = {
    'out_invoice': 'Tax Invoice',
    'out_refund': 'Credit Note'
}


class AccountTax(models.Model):
    _inherit = 'account.tax'

    esd_tax_band = fields.Selection(string='Vat Tax Band',
                                    selection=[('A', 'Vat A'), ('B', 'Vat B'), ('C', 'Vat C'), ('D', 'Vat D'),
                                               ('E', 'Vat E')], copy=False)

    @api.constrains('esd_tax_band')
    def _constrains_esd_tax_band(self):
        for rec in self.filtered('esd_tax_band'):
            tax_bands = self.env['account.tax'].search(
                [('id', '!=', rec.id), ('esd_tax_band', '=', rec.esd_tax_band),
                 ('type_tax_use', '=', rec.type_tax_use)])
            if tax_bands:
                raise ValidationError(
                    'You cannot have more than one vat tax with the Current Vat Tax Band set in the same Tax Type!')


class AccountMOve(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'oo.esd.api']
    
    
    def action_sign_invoice(self):
        for rec in self.filtered(lambda r: INVOICE_MAP.get(r.move_type) and r.company_id.esd_enable):
            if rec.state in ('draft', 'cancelled'): # or rec.esd_qr_code:
                raise ValidationError('You can only sign a validated/unsigned invoice!')
            if rec.esd_signature:
                raise ValidationError(f'Invoice {rec.name} is signed!')
            rec._sign_invoice()
        if self.filtered(lambda r: r.move_type in ('in_invoice', 'in_refund', 'entry')):
            raise ValidationError('You can only sign customer invoices and refunds!')
            
        return True

    is_export = fields.Boolean(string='Export Invoice')
    export_hscode_id = fields.Many2one('product.hscode', string='Export HSCode')

    use_manual_fx = fields.Boolean(string='Use Manual FX RATE')
    manual_rate = fields.Float(string='FX Rate', help="The Rate the from currency trades with the to currency")
    esd_signature = fields.Char(string='ESD Signature', readonly=True, copy=False)
    esd_qr_code = fields.Binary(string='Esd QR Code', copy=False, attachment=True, readonly=True)
    esd_date_signed = fields.Datetime(string='Esd Date Signed', readonly=True, copy=False)
    esd_device_serial = fields.Char(string='Esd Device Serial', readonly=True, copy=False)
    esd_currency_id = fields.Many2one('res.currency', string='Ksh Currency', compute='_compute_esd_currency_id')
    esd_total_signed = fields.Monetary(string='Total Amount Signed', copy=False,
                                       currency_field='esd_currency_id', readonly=True)
    
    @api.constrains('manual_rate')
    def _constrains_manual_rate(self):
        kes = self.env['res.currency'].search([('name', '=', 'KES')], limit=1)
        for rec in self:
            if rec.use_manual_fx and kes.is_zero(rec.manual_rate):
                raise ValidationError('The manual exchange cannot be zero!')

    def _compute_esd_currency_id(self):
        kes = self.env['res.currency'].search([('name', '=', 'KES')], limit=1)
        for rec in self:
            rec.esd_currency_id = kes.id


class AccountMOveLine(models.Model):
    _inherit = 'account.move.line'

    is_esd_signed = fields.Boolean(string='Is Esd Signed')
    price_unit_kes = fields.Float(string='Price Unit (KSH)', compute='_compute_price_kes')
    price_total_kes = fields.Float(string='Price Total (KSH)')
    price_subtotal_kes = fields.Float(string='Price Subtotal (KSH)')
    hscode_id = fields.Many2one('product.hscode', string='Product HSCode', compute="_compute_hscode_id", store=True)

    @api.depends('price_unit', 'currency_id')
    def _compute_price_kes(self):
        for rec in self:
            rec.price_unit_kes = rec.move_id._currency_convert(rec.price_unit)
            rec.price_subtotal_kes = rec.move_id._currency_convert(rec.price_subtotal)
            rec.price_total_kes = rec.move_id._currency_convert(rec.price_total)
    
    @api.depends('product_id', 'move_id.is_export', 'move_id.export_hscode_id')
    def _compute_hscode_id(self):
        for line in self:
            line.hscode_id = False
            hscode = line.product_id.hscode_id
            if line.move_id.is_export and line.move_id.export_hscode_id:
                hscode = line.move_id.export_hscode_id
            if hscode:
                tax_id = [(6, 0, [hscode.tax_id.id])] or False
                line.update({'hscode_id': hscode.id, 'tax_ids': tax_id})

