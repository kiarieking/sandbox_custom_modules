import json
from odoo import api, models, fields, _ 
from odoo.exceptions import UserError

class GeneralDispatchStatementsWizard(models.TransientModel):
    _name = 'customer.revenue.cost.wizard'
    _description = 'customer.revenue.cost.wizard'

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

        return self.env['customer.revenue.cost.report'].action_generate_report(self, data=data)

class GeneralDispatchStatementsReport(models.AbstractModel):
    _name = 'customer.revenue.cost.report'
    _description = 'customer.revenue.cost.report'

    def action_generate_report(self, docids, data=None):
        '''Action to generate report'''

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        domain=[]

        if date_start and date_end:
            domain = [
                ("date_dispatch", '>=', date_start),
                ("date_dispatch", "<=", date_end),]
        if (date_start and not date_end) or (not date_start and date_end):
            raise UserError("Enter start and end date!")

        non_lpo_dispatch_ledgers = self.env["quatrix.dispatch"].search(domain)
        lpo_dispatch_ledgers = self.env["purchase.dispatch"].search(domain)

        currency_id = None
        dispatch_ledgers = []
        ledgers = []

        for ledger in lpo_dispatch_ledgers: dispatch_ledgers.append(ledger)
        for ledger in non_lpo_dispatch_ledgers: dispatch_ledgers.append(ledger)
        
        partner_ids = set()

        for dispatch_ledger in dispatch_ledgers:
            partner_ids.add(dispatch_ledger.partner_id)
            currency_id = dispatch_ledger.currency_id

        total_carrier_charges = 0
        total_amount = 0
        
        for partner_id in partner_ids:
            partner_record = {"carrier_charges": 0, "amount_total": 0, "margin": 0, "margin_percentage" : 0}
            for dispatch_ledger in dispatch_ledgers:
                if partner_id == dispatch_ledger.partner_id:
                    partner_record["partner_name"] = dispatch_ledger.partner_id.name
                    partner_record["carrier_charges"] += dispatch_ledger.carrier_charges
                    partner_record["amount_total"] += dispatch_ledger.amount
            ledgers.append(partner_record)
        
        for ledger in ledgers:
            ledger_amount = ledger["amount_total"]
            total_carrier_charges += ledger["carrier_charges"]
            total_amount += ledger["amount_total"]
            diff = ledger["amount_total"] - ledger["carrier_charges"]

            ledger["margin"] = diff

            if ledger_amount > 0:
                ledger["margin_percentage"] = ((diff/ledger_amount) * 100)
        
        net_total = total_amount - total_carrier_charges

        docs = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'currency_id': currency_id,
            'order_ids':ledgers,
            "total_amount": total_amount,
            "total_cost":total_carrier_charges,
            "total_margin": net_total
        }

        # raise UserError((ledgers))

        return self.env.ref('quatrix_dispatch_module.customer_revenue_cost_report').report_action(self, data=docs, config=False)
