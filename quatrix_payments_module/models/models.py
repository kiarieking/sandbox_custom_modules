'''Process payments model'''
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    '''Inherit Account move'''
    _inherit = 'account.move'

    @api.depends('state')
    def assign_outstanding(self):
        self.ensure_one()
        line_ids = self.env['account.move.line'].search([])

        for line_id in line_ids:
            outstanding_id = self.env['account.move'].sudo().js_assign_outstanding_line(line_id)
            return outstanding_id

    # @api.onchange('state')
    def action_post(self):
        self.ensure_one()

        res = super(AccountMove, self).action_post()

        partial_deductions = []
        full_deductions = []

        installment_percentage = int(self.env['ir.config_parameter'].sudo().get_param(
            'quatrix_inheritance_module.payment_installment_id') or False)
        full_percentage = int(self.env['ir.config_parameter'].sudo().get_param(
            'quatrix_inheritance_module.payment_full_id') or False)

        account_recievable = self.env['account.account'].search([('code', '=', '121000')])
        account_payable = self.env['account.account'].search([('code', '=', '211000')])
        payment_term = self.env['account.payment.term'].search([('name', '=', 'Installments')])

        # raise UserError(payment_term.id)

        for record in self:
            invoices = self.env['account.move'].search([('move_type', '=', 'out_invoice'),
            ('partner_id','=', record.partner_id.id), ('state', '=', 'posted')])

            for invoice in invoices:
                if invoice.invoice_payment_term_id.id == payment_term.id:
                    if invoice.amount_residual > 0:
                        partial_deductions.append(invoice)
                if invoice.invoice_payment_term_id.id != payment_term.id:
                    if invoice.amount_residual > 0:
                        full_deductions.append(invoice)

            if record.move_type == 'in_invoice' and record.state == 'posted' and ((partial_deductions is not None) or (full_deductions is not None)):

                for rec in partial_deductions:

                    amount_residual = 0

                    amount_to_deduct = abs(record.amount_residual * (installment_percentage/100))

                    if rec.amount_residual < amount_to_deduct:
                        amount_residual = rec.amount_residual
                    else:
                        amount_residual = amount_to_deduct

                    debit_vals = {
                        'name': "CUST.IN/"+record.name,
                        'debit': abs(amount_residual),
                        'credit': 0.0,
                        'partner_id': rec.partner_id.id,
                        'account_id': account_payable.id,
                    }

                    credit_vals = {
                        'name': "Customer Payment : " + rec.name,
                        'debit': 0.0,
                        'credit': abs(amount_residual),
                        'partner_id': rec.partner_id.id,
                        'account_id': account_recievable.id,
                    }

                    vals = {
                        'move_type': 'entry',
                        'journal_id': record.journal_id.id,
                        # 'name': "Partial Deduction: " + record.name + '/' + rec.name,
                        'ref': rec.name,
                        'date': record.date,
                        'state': 'draft',
                        'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
                    }

                    # Add function to check if the journal exists.

                    move_id = self.env['account.move'].create(vals)
                    move_id.post()

                for rec in full_deductions:

                    amount_residual = 0

                    amount_to_deduct = abs(record.amount_residual * (full_percentage/100))

                    if rec.amount_residual > record.amount_residual:
                        amount_residual = record.amount_residual
                    else:
                        amount_residual = rec.amount_residual
                    
                    debit_vals = {
                        'name': "CUST.IN/"+record.name,
                        'debit': abs(amount_residual),
                        'credit': 0.0,
                        'partner_id': rec.partner_id.id,
                        'account_id': account_payable.id,
                    }

                    credit_vals = {
                        'name': "Customer Payment :" + rec.name,
                        'debit': 0.0,
                        'credit': abs(amount_residual),
                        'partner_id': rec.partner_id.id,
                        'account_id': account_recievable.id,
                    }

                    vals = {
                        'move_type': 'entry',
                        'journal_id': record.journal_id.id,
                        # 'name': "Full Deduction: " + record.name + '/' + rec.name,
                        'ref': rec.name,
                        'date': record.date,
                        'state': 'draft',
                        'line_ids': [(0, 0, credit_vals), (0, 0, debit_vals)]
                    }

                    move_id = self.env['account.move'].create(vals)
                    move_id.post()
                    # self.assign_outstanding()
        return res

    @api.onchange('state')
    @api.depends('state')
    def check_cancelled_invoices(self):
        '''Cancel journals whose invoices have been cancelled.'''
        invoice_refs = []

        for record in self:
            invoices = self.env['account.move'].search([('move_type', '=', 'out_invoice'),
                ('partner_id','=', record.partner_id.id)])
            for invoice in invoices:
                if (record.move_type == 'out_invoice' and record.state == 'cancel') or(record.move_type == 'out_invoice' and record.state == 'draft'):
                    invoice_refs.append(invoice.name)
        
        for ref in invoice_refs:
            entries = self.env['account.move'].search([
                ('move_type', '=', 'entry'),
                ('partner_id','=', record.partner_id.id),
                ('state', '=', 'cancel'),
                ('ref', '=', ref)
                ])
            for entry in entries:
                try:
                    self.env['account.move'].search([('id', '=', entry.id)]).unlink() or entry.unlink(entry.id)
                except Exception as e:
                    raise UserError(_(e))
