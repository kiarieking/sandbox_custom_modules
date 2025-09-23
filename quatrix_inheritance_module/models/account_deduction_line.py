import logging
from datetime import datetime

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)
class PaymentLines(models.Model):
    _name = 'account.deduction.line'
    _description = 'account.deduction.line'

    deduction_id =fields.Many2one('account.move', required=True, ondelete="restrict")
    invoice_to_deduct = fields.Many2one('account.move', string="Document Ref")
    date_deduction = fields.Date("Date", default=datetime.now())
    amount_pending = fields.Float("Amount")
    amount_to_deduct = fields.Float("Deduction/Payment", default=0.0)
    description = fields.Char("Description", default="")

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

class PaymentProcessing(models.Model):
    _inherit = 'account.move'

    deduction_line_ids = fields.One2many('account.deduction.line', 'deduction_id')
    deduction_amount_total = fields.Float("Deductions", default=0.0, compute="_compute_deduction_amount")
    amount_to_deduct = fields.Float(related="deduction_line_ids.amount_to_deduct")

    @api.depends('amount_to_deduct')
    @api.onchange('amount_to_deduct')
    def _compute_deduction_amount(self):
        '''Compute deduction amount total'''
        deduction_amount = 0
        for record in self:
            for line in record.deduction_line_ids:
                deduction_amount += line.amount_to_deduct
        record.deduction_amount_total = deduction_amount
    
    def _check_amount_before_deduction(self):
        '''Check if amount to be deducted is greater than invoice amount.'''
        for record in self:
            if record.deduction_amount_total > record.amount_total:
                raise UserError("Deduction cannot be greater than amount total.")

    def button_draft(self):
        '''Restrict deletion of records with active deduction journal entries'''
        res = super(PaymentProcessing, self).button_draft()

        inv_names = [self.name]

        for record in self:
            for invoices in record.deduction_line_ids:
                for line in invoices:
                    inv_names.append(line.invoice_to_deduct.name)

        journals = self.env['account.move'].search([('move_type','=','entry'),('ref','in',inv_names)])

        if journals:
            for journal in journals:
                if journal.state != 'cancel':
                    raise UserError("Unauthorized. A journal exists for the deductions made for this record!")
                    
        return res

    def action_cancel(self):
        '''Restrict deletion of records with active deduction journal entries'''

        res = super(PaymentProcessing, self).action_cancel()
        journals = self.env['account.move'].search([('move_type','=','entry'),('ref','=',self.name)])

        if journals:
            for journal in journals:
                if journal.state != 'cancel':
                    raise UserError("Unauthorized. A journal exists for the deductions made for this record!")

        return res


    def action_post(self):
        '''Inherit action post'''
        res = super(PaymentProcessing, self).action_post()

        cust_invoices = self.env['account.move'].search([
            ('move_type','=','out_invoice'),
            ('state','=','posted'),
            ('partner_id','=',self.partner_id.id)
        ])
        
        if self.state == 'cancel':
            return res

        self._check_amount_before_deduction()

        for line in self.deduction_line_ids:
            for cust_inv in cust_invoices:
                if line.invoice_to_deduct.name == cust_inv.name:
                    vals = [(0,0,{
                        'invoice_to_deduct': self.id,
                        'amount_to_deduct': line.amount_to_deduct,
                        'amount_pending': cust_inv.amount_total,
                        'description': 'payment from ' + self.name
                    })]

                    if cust_inv.amount_residual > 0:
                        cust_inv.write({'deduction_line_ids': vals})
        self.make_payments()
    
    def make_payments(self):
        '''Make deductions and post deductions to journals'''
        account_recievable = self.env['account.account'].search([('code', '=', '121000')])
        account_payable = self.env['account.account'].search([('code', '=', '211000')])

        move_id = None

        for record in self:
            for line in record.deduction_line_ids:
                invs = self.env['account.move'].search([('name','=',line.invoice_to_deduct.name)])
                
                for inv in invs:
                    debit_vals = {
                        'name': record.name,
                        'debit': abs(line.amount_to_deduct),
                        'credit': 0.0,
                        'partner_id': record.partner_id.id,
                        'account_id': account_payable.id,
                    }

                    credit_vals = {
                        'name': inv.name,
                        'debit': 0.0,
                        'credit': abs(line.amount_to_deduct),
                        'partner_id': record.partner_id.id,
                        'account_id': account_recievable.id,
                    }

                    vals = {
                            'move_type': 'entry',
                            'journal_id': record.journal_id.id,
                            'ref': inv.name,
                            'date': record.date,
                            'state': 'draft',
                            'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
                        }
                    
                    checks = [inv.name, record.name]

                    journals = self.env['account.move'].search([('move_type','=','entry'),('ref','in',checks)])

                    if journals:
                        for journal in journals:
                            if journal.state != 'cancel':
                                return
                            if journal.state == 'cancel':
                                move_id = self.env['account.move'].create(vals)
                    else:
                        move_id = self.env['account.move'].create(vals)
                    move_id.post()

                    for move in move_id:
                        for move_line in move.line_ids:
                            if move_line.account_id == account_payable:
                                self.js_assign_outstanding_line(move_line.id)
                            if move_line.account_id == account_recievable:
                                inv.js_assign_outstanding_line(move_line.id)

    @api.onchange('invoice_line_ids')
    def populate_deduction_lines(self):
        '''Populate deductions lines with fuel data when a new supplier invoice is created'''

        if self.move_type != 'in_invoice':
            return

        order_nos = []
        dispatch_names = []
        fuel_names = []

        for record in self:
            for line in record.invoice_line_ids:
                order_nos.append(line.order_no)

        for order_no in order_nos:
            dispatch_line = self.env['quatrix.dispatch.line'].search([('order_no','=',order_no)])
            

            if dispatch_line:
                dispatch = self.env['quatrix.dispatch'].search([('id','=',dispatch_line.order_id.id)])
                dispatch_names.append(dispatch.name)
        
        for name in dispatch_names:
            fuel_order = self.env['fuel.voucher'].search([('reference_number','=', name)])
            if fuel_order:

                for order in fuel_order:
                    fuel_names.append(order.name)

        lines = []
        inv_ids = []

        fuel_invoices = self.env['account.move'].search([('move_type','=','out_invoice'),('partner_id','=', self.partner_id.id), ('ref','in',fuel_names), ('amount_residual','>',0)])
        if not fuel_invoices:
            return
    
        for inv in fuel_invoices:
            date = None

            for line in inv.invoice_line_ids:
                date = line.dates

            vals = [(0,0, {
                "date_deduction": date,
                "invoice_to_deduct": inv.id,
                "amount_to_deduct": inv.amount_residual,
                'amount_pending': inv.amount_total
            })]

            if inv.id not in inv_ids:
                lines.append(vals)
            inv_ids.append(inv.id)

        for line in lines:
            self.write({"deduction_line_ids": line})
