import logging

from odoo import api, models, fields, _ 
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
class AcountingRevenueWizard(models.TransientModel):
    _name = 'accounting.revenue.cost.wizard'
    _description = 'accounting.revenue.cost.wizard'

    date_start = fields.Date('Start Date', required=False)
    date_end = fields.Date("End Date", required=False)
    partner_id = fields.Many2one('res.partner', string="Partner", required=False)

    def get_values(self):
        '''Get Value from wizard'''

        ids = self.env[self._name].search([])

        if not ids:
            if not isinstance(ids, list):
                ids = [ids]
        context = dict(self.env.context or {}, active_ids=ids.ids, active_model=self._name)

        data = {
            'ids':self.id,
            'model':self._name,
            'context':context,
            'lines':ids,
            'form': {
                'date_start':self.date_start,
                'date_end':self.date_end,
                'partner_id':self.partner_id.id,
                'partner':self.partner_id.name
                }
            }

        return self.env['accounting.revenue.cost'].action_generate_report(self, data=data)

class AccountingRevenueReport(models.AbstractModel):
    _name = 'accounting.revenue.cost'
    _description = 'accounting.revenue.cost'

    def action_generate_report(self, docids, data=None):
        '''Action to generate report'''

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        partner_id = data['form']['partner_id']
        partner = data['form']['partner']

        if date_start and not date_end:
            raise UserError("Please enter the end date")

        if date_end and not date_start:
            raise UserError("Please enter the start date")

        domain = [("state", "!=", 'draft')]

        if not partner_id and date_start and date_end:
            domain = [
                ("invoice_date", '>=', date_start),
                ("invoice_date", "<=", date_end),
                ("state", "!=", 'draft')]
        if partner_id and date_start and date_end:
            domain = [
                ('partner_id', '=', partner_id),
                ("invoice_date", '>=', date_start),
                ("invoice_date", "<=", date_end),
                ("state", "!=", 'draft')
            ]
        
        if partner_id and not date_start and not date_end:
            domain = [
                ('partner_id', '=', partner_id),
                ("state", "!=", 'draft')
            ]

        account_ledgers = self.env["account.move"].search(domain)

        amount_total = 0.0
        total_margin =  0.0
        total_cost = 0.0

        currency_id = None

        ledgers = []

        
        for account_ledger in account_ledgers:
            record = {}

            for line in account_ledger.invoice_line_ids:
                margin = 0

                if line.product_id:

                    if line.product_id.list_price > 0 and line.price_subtotal > 0:
                        margin = (line.product_id.list_price - line.product_id.standard_price) * line.quantity
                        margin_percentage = ((line.price_subtotal - margin)/line.price_subtotal) * 100
                    record["date"] = str(line.date)
                    record["product"] = line.product_id.name
                    record["partner"] = line.partner_id.name
                    record["reference"] = line.order_no
                    record["amount_cost"] = (line.product_id.list_price) * line.quantity
                    record["carrier_cost"] = line.product_id.standard_price * line.quantity
                    record["quantity"] = line.quantity
                    record["margin"] = margin
                    record["margin_percentage"] = 100 - margin_percentage

                    record['currency_id'] = account_ledger.currency_id
                    currency_id = account_ledger.currency_id.symbol

            if len(record) != 0:
                ledgers.append(record)

        for ledger in ledgers:
            amount_total += float(ledger["amount_cost"])
            total_margin += float(ledger["margin"])
            total_cost += float(ledger["carrier_cost"])

    
        docs = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'partner':partner,
            'partner_id': partner_id,
            'currency_id': currency_id,
            'order_ids':ledgers,
            'total_margin': float(total_margin),
            'total_amount': float(amount_total),
            'total_cost': float(total_cost)
        }

        for order_id in docs["order_ids"]:
            _logger.info(order_id)

        return self.env.ref('quatrix_inheritance_module.accounting_revenue_cost').report_action(self, data=docs, config=False)
