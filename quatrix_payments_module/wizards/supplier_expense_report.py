from odoo import api, models, fields, _ 
from odoo.exceptions import UserError

class GeneralSupplierStatementWizard(models.TransientModel):
    _name = 'supplier.report.wizard'
    _description = 'supplier.report.wizard'

    date_start = fields.Date('Start Date')
    date_end = fields.Date("End Date")

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
                }
            }

        return self.env['supplier.report'].action_generate_report(self, data=data)


class GeneralDispatchStatementsReport(models.AbstractModel):
    _name = 'supplier.report'

    def action_generate_report(self, docids, data=None):
        '''Action to generate report'''

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        total_amount = 0
        untaxed_total_amount = 0
        currency_id = None

        domain=[('move_type', '=', 'in_invoice'), ('state', '!=', 'draft')]

        if date_start and date_end:
            domain = [
                ("date", '>=', date_start),
                ("date", "<=", date_end),
                ('move_type', '=', 'out_invoice'),
                ('state', '!=', 'draft')
                ]

        account_ledgers = self.env["account.move"].search(domain)
        ledgers = []

        for ledger in account_ledgers:
            docs = {}

            docs['state'] = ledger.state
            docs['date'] = ledger.date
            docs['name'] = ledger.name
            docs['amount_untaxed'] = ledger.amount_untaxed
            docs['amount_total'] = ledger.amount_total
            docs['partner_id'] = ledger.partner_id.name
            currency_id = ledger.currency_id

            ledgers.append(docs)

        for ledger in ledgers:
            total_amount += ledger["amount_total"]
            untaxed_total_amount += ledger['amount_untaxed']


        docs = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'currency_id': currency_id,
            'order_ids': ledgers,
            "untaxed_amount_total": untaxed_total_amount,
            "amount_total": total_amount,
        }

        # raise UserError(docs)

        return self.env.ref('quatrix_payments_module.supplier_report_statement').report_action(self, data=docs, config=False)