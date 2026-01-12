from datetime import datetime
from odoo import fields, api, models, _
from odoo.exceptions import UserError

class PartnerLedger(models.TransientModel):
    '''Create a wizard for partner Ledger'''
    _name = 'partner.fuel.wizard'
    _description = 'Create a wizard for partner Ledger'

    date_start = fields.Date(string="From", required=True)
    date_end = fields.Date(string="To", required=True)
    carrier_id = fields.Many2one('res.partner', string="Carrier", required=False)

    def get_values(self):
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
                'carrier_id':self.carrier_id.id,
                'carrier':self.carrier_id.name
                }
            }

        return self.env['report.partner.ledger'].action_generate_report(self, data=data)

class PartnerLedgerReport(models.AbstractModel):
    '''Partner report for Fuel Ledgers'''
    _name = "report.partner.ledger"
    _description = "Partner report for Fuel Ledgers"

    def action_generate_report(self, docids, data=None):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        carrier_id = data['form']['carrier_id']
        carrier = data['form']['carrier']

        domain = []

        order_lines = []

        if carrier:
            domain = [("date", '>=', date_start), ("date", "<=", date_end), ('carrier_id', '=', carrier_id)]
        else:
            domain = [("date", '>=', date_start), ("date", "<=", date_end)]

        partner_ledgers = self.env["fuel.voucher"].search(domain, order='date asc')

        amount_total = 0.0
        total_quantity = 0.0
        ledger_info = {}
        currency_id = None

        if not partner_ledgers:
            raise UserError(_("No record found for the time period!"))
        
        for ledger in partner_ledgers:
            amount_total += ledger.amount_total

            quantity = 0
            price_unit = 0
            description = ""
            narration = ""
            product = ""

            record = {}

           

            for line in ledger.order_ids:
                quantity += line.quantity
                price_unit = line.price_unit
                product = line.product_id.name

                if not description: description = line.description
                if not narration: description = line.narration
            
            record["quantity"] = quantity
            record["price_unit"] = price_unit
            record["product"] = product
            record["description"] = description
            record["narration"] = narration

            record["date"] = ledger.date
            record["reference"] = ledger.reference_number
            record["vehicle"] = ledger.vehicle_id.license_plate
            record["currency_id"] = ledger.currency_id

            for order_id in ledger.order_ids:
                total_quantity += order_id.quantity

            currency_id = ledger.currency_id.symbol

            order_lines.append(record)

        docs = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'carrier':carrier,
            'currency_id': currency_id,
            'carrier_id': carrier_id,
            'order_ids':order_lines,
            'amount_total': float(amount_total),
            'total_quantity': total_quantity
        }

        # raise UserError(_(docs))

        return self.env.ref('fuel_voucher_module.report_partner_ledger').report_action(self, data=docs, config=False)
