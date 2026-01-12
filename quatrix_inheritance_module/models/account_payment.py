import logging

from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class AccountPayment(models.Model):
    _inherit = "account.payment"

    other_ref = fields.Char("MPESA Ref", help="MPESA Reference/Receipt No etc")
    invoices_to_offset = fields.Many2many("account.move", string="Invoices", help="Use this feature while making multiple mayments and only if you dont have pending customer debits.")

    @api.onchange('state','invoices_to_offset', 'amount', 'payment_type')
    def _offset_invoices_against_payment(self):
        '''Offset pending payments'''
        account_recievable = self.env['account.account'].search([('code', '=', '121000')])

        for record in self:
            if record.state != 'posted':
                return
            move_line = self.env['account.move.line'].search([('name','=',self.name)])
            moves = self.env["account.move"].search([('id', '=', move_line.move_id.id)])

            if record.invoices_to_offset is not None:
                for inv in record.invoices_to_offset:
                    for move in moves:
                        for line in move.line_ids:
                            if line.account_id == account_recievable:
                                inv.js_assign_outstanding_line(line.id)

    def post(self):
        res = super(AccountPayment, self).post()
        for record in self:
            record._offset_invoices_against_payment()
        return res
    
    @api.model
    def _compute_payment_amount(self, invoices, currency, journal, date):
        '''Compute the total amount for the payment wizard.
        :param invoices:    Invoices on which compute the total as an account.invoice recordset.
        :param currency:    The payment's currency as a res.currency record.
        :param journal:     The payment's journal as an account.journal record.
        :param date:        The payment's date as a datetime.date object.
        :return:            The total amount to pay the invoices.
        '''

        res = super(AccountPayment, self)._compute_payment_amount(invoices, currency, journal, date)

        company = journal.company_id
        currency = currency or journal.currency_id or company.currency_id
        date = date or fields.Date.today()

        if not invoices:
            return 0.0

        self.env['account.move'].flush(['move_type', 'currency_id'])
        self.env['account.move.line'].flush(['amount_residual', 'amount_residual_currency', 'move_id', 'account_id'])
        self.env['account.account'].flush(['user_type_id'])
        self.env['account.account.type'].flush(['type'])
        self._cr.execute('''
            SELECT
                move.name as name,
                move.move_type AS type,
                move.currency_id AS currency_id,
                SUM(line.amount_residual) AS amount_residual,
                SUM(line.amount_residual_currency) AS residual_currency
            FROM account_move move
            LEFT JOIN account_move_line line ON line.move_id = move.id
            LEFT JOIN account_account account ON account.id = line.account_id
            LEFT JOIN account_account_type account_type ON account_type.id = account.user_type_id
            WHERE move.id IN %s
            AND account_type.type IN ('receivable', 'payable')
            GROUP BY move.id, move.move_type
        ''', [tuple(invoices.ids)])
        
        query_res = self._cr.dictfetchall()

        total = 0.0

        for res in query_res:  
            amount_residual = res["amount_residual"]

            move_currency = self.env['res.currency'].browse(res['currency_id'])
            if move_currency == currency and move_currency != company.currency_id:
                total += res['residual_currency']
            else:
                total += company.currency_id._convert(amount_residual, currency, company, date)
        return total
