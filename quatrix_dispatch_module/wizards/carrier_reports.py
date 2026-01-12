from odoo import api, models, fields, _ 
from odoo.exceptions import UserError

class CarrierReportStatementsWizard(models.TransientModel):
    _name = 'carrier.report.wizard'
    _description = 'carrier.report.wizard'

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

        return self.env['carrier.report'].action_generate_report(self, data=data)

class CarrierReportStatementsReport(models.AbstractModel):
    _name = 'carrier.report'
    _description = 'carrier.report'

    def action_generate_report(self, docids, data=None):
        '''Action to generate report'''

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        domain = []
        partners = []
        

        if date_start and date_end:
            domain = [
                ("date_dispatch", '>=', date_start),
                ("date_dispatch", "<=", date_end),]

        ledgers = self.env['quatrix.dispatch'].search(domain)

        for ledger in ledgers:
            partners.append(ledger.vendor_id)

        account_ledgers = []
        vehicles = []

        vehicleInfo = []
        info = []
        

        for partner in partners:
            account_ledgers = self.env["account.move"].search([("partner_id", "=", partner.id)])
            vehicles = self.env["fleet.vehicle"].search([('carrier_carrier_id', '=', partner.carrier_carrier_id)])
            # for move in moves:
            #     account_ledgers.append(move)

            if len(account_ledgers) == 0:
                raise UserError("No record found.")

            vehicles_info = {}
            for vehicle in vehicles:
                vehicles_info[vehicle.carrier_carrier_id] = vehicle.license_plate
                vehicleInfo.append(vehicles_info)

            
            for acc in account_ledgers:
                Gross = {}
                Deductions = {}
                
                if acc.move_type == 'in_invoice' or acc.move_type == 'in_refund':
                    if acc.partner_id.id in Gross:
                        Gross[acc.partner_id.id] += acc.amount_residual
                    else:
                        Gross[acc.partner_id.id] = acc.amount_residual


                if acc.move_type == 'out_invoice' or acc.move_type == 'out_refund':
                    if acc.partner_id.id in Deductions:
                        Deductions[acc.partner_id.id] += acc.amount_residual
                    else:
                        Deductions[acc.partner_id.id] = acc.amount_residual

                for acc_ledger in account_ledgers:
                    res = {}
                    gross = 0
                    deductions = 0
                    try:
                        if not Gross[acc_ledger.partner_id.id]:
                            gross = 0
                        else:
                            gross = Gross[acc_ledger.partner_id.id]
                    except:
                        gross = 0

                    try:
                        if not Deductions[acc_ledger.partner_id.id]:
                            deductions = 0
                        else:
                            deductions = Deductions[acc_ledger.partner_id.id]
                    except:
                        deductions = 0

                    if acc_ledger.partner_id.carrier_carrier_id in vehicles_info:

                        res["vehicle"] = vehicles_info[acc_ledger.partner_id.carrier_carrier_id]
                        res["carrier"] = acc_ledger.partner_id.name
                        res["gross"] = gross
                        res["deductions"] = deductions
                        res["net"] = gross - deductions

                        if res not in info:
                            info.append(res)

        currency_id = None

        for dispatch_ledger in ledgers:
            currency_id = dispatch_ledger.currency_id.symbol
    
        docs = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'currency_id': currency_id,
            'order_ids':info,
        }

        # raise UserError(account_ledgers)

        return self.env.ref('quatrix_dispatch_module.carrier_report_statement').report_action(self, data=docs, config=False)
