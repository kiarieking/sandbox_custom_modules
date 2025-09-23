from datetime import datetime
from odoo import fields, api, models, _
from odoo.exceptions import UserError

class PartnerLedger(models.TransientModel):
    '''Create a wizard for partner Ledger'''
    _name = 'partner.billing.wizard'
    _description = 'partner.billing.wizard'

    date_start = fields.Date(string="From", required=True)
    date_end = fields.Date(string="To", required=True)
    carrier_id = fields.Many2one('res.partner', string="Carrier", required=True)

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

        return self.env['report.partner.billing.ledger'].action_generate_report(self, data=data)

class PartnerLedgerReport(models.AbstractModel):
    '''Partner report for Fuel Ledgers'''
    _name = "report.partner.billing.ledger"
    _description = "Partner report for Fuel Ledgers"

    # @api.model
    def action_generate_report(self, docids, data=None):

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        carrier_id = data['form']['carrier_id']
        carrier = data['form']['carrier']

        order_lines = []

        domain = [("date_billing", '>=', date_start), ("date_billing", "<=", date_end), ('partner_id', '=', carrier_id)]

        partner_ledgers = self.env["billing.order"].search(domain, order='date_billing asc')

        amount_total = 0.0
        ledger_info = {}
        currency_id = None
        

        if not partner_ledgers:
            raise UserError(_("No record found for the selected partner or the time period!"))
        
        for ledger in partner_ledgers:
            amount_total += ledger.amount_total

            record = {}

            record["product"] = ledger.order_line.product_id.name
            record["narration"] = ledger.order_line.notes
            record["quantity"] = ledger.order_line.quantity
            record["price_unit"] = ledger.order_line.price_unit
            record["date"] = ledger.date_billing
            record["reference"] = ledger.reference_number
            record["vehicle"] = ledger.vehicle_id.license_plate
            record["currency_id"] = ledger.currency_id

            if ledger.vehicle_id.license_plate and ledger.order_line.name:
                record["description"] = ledger.vehicle_id.license_plate + " - " +ledger.order_line.name
            else:
                record["description"] = ledger.order_line.name or ledger.vehicle_id.license_plate
               
            currency_id = ledger.currency_id.symbol

            order_lines.append(record)

        docs = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'carrier':carrier,
            'carrier_id': carrier_id,
            'currency_id': currency_id,
            'order_ids':order_lines,
            'amount_total': float(amount_total)
        }

        return self.env.ref('quatrix_billing_module.report_partner_billing_ledger').report_action(self, data=docs, config=False)