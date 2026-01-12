from odoo import api, models, fields, _ 
from odoo.exceptions import UserError

class GeneralDispatchStatementsWizard(models.TransientModel):
    _name = 'dispatch.general.wizard'
    _description = 'dispatch.general.wizard'

    date_start = fields.Date('Start Date')
    date_end = fields.Date("End Date")
    partner_id = fields.Many2one('res.partner', string="Customer/Shipper")

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

        return self.env['dispatch.general.report'].action_generate_report(self, data=data)

class GeneralDispatchStatementsReport(models.AbstractModel):
    _name = 'dispatch.general.report'
    _description = 'dispatch.general.report'

    def action_generate_report(self, docids, data=None):
        '''Action to generate report'''

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        partner_id = data['form']['partner_id']
        partner = data['form']['partner']

        domain=[]

        if partner_id and date_start and date_end:
            domain = [
                ('partner_id', '=', partner_id),
                ("date_dispatch", '>=', date_start),
                ("date_dispatch", "<=", date_end),]
        if not partner_id and date_start and date_end:
            domain = [
                ("date_dispatch", '>=', date_start),
                ("date_dispatch", "<=", date_end),]
        if partner_id and not date_start and not date_end:
            domain = [('partner_id', '=', partner_id),]

        non_lpo_dispatch_ledgers = self.env["quatrix.dispatch"].search(domain)
        lpo_dispatch_ledgers = self.env["purchase.dispatch"].search(domain)
        dispatch_ledgers = []

        for ledger in lpo_dispatch_ledgers:
            dispatch_ledgers.append(ledger)
        for ledger in non_lpo_dispatch_ledgers:
            dispatch_ledgers.append(ledger)

        ledgers = []
        currency_id = None

        for dispatch_ledger in dispatch_ledgers:
            record = {}
            margin = 0
            
            record['date'] = (dispatch_ledger.date_dispatch).strftime("%d/%m/%Y")
            record["customer"] = dispatch_ledger.partner_id.name
            record["vehicle"] = dispatch_ledger.vehicle_id.license_plate
            record["line"] = dispatch_ledger.order_ids
            record["amount_total"] = dispatch_ledger.amount
            record["carrier_charges"] = dispatch_ledger.carrier_charges
            record["loading_charges"] = dispatch_ledger.loading_charges

            margin = dispatch_ledger.amount - (dispatch_ledger.carrier_charges + dispatch_ledger.loading_charges)
              
            record["margin"] = margin

            if dispatch_ledger.amount != 0:
                record["margin_percentage"] = ((margin)/dispatch_ledger.amount)*100
            else:
                record["margin_percentage"] = 0
            route = ""
            for line in dispatch_ledger.order_ids:
                if route == "":
                    route =  line.product_id.name
                else:
                    route +=  "/" + line.product_id.name
            record["route"] = route

            ledgers.append(record)

        for dispatch_ledger in dispatch_ledgers:
            currency_id = dispatch_ledger.currency_id.symbol
        
        total_amount = 0
        total_carrier_charges = 0
        total_loading_charges = 0
        

        for ledger in ledgers:
            total_amount += ledger["amount_total"]
            total_carrier_charges += ledger["carrier_charges"]
            total_loading_charges += ledger["loading_charges"]
        
        total_margin = total_amount - (total_loading_charges + total_carrier_charges)
        total_cost = total_loading_charges + total_carrier_charges
        
        docs = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'partner':partner,
            'partner_id': partner_id,
            'currency_id': currency_id,
            'order_ids':ledgers,
            "total_amount": total_amount,
            "total_carrier_charges":total_carrier_charges,
            "total_loading_charges":total_loading_charges,
            "total_margin":total_margin,
            "total_cost":total_cost
        }

        return self.env.ref('quatrix_dispatch_module.general_report_statement').report_action(self, data=docs, config=False)
