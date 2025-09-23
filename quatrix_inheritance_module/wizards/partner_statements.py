from odoo import api, models, fields, _ 
from odoo.exceptions import UserError

class PartnerStatementsWizard(models.TransientModel):
    _name = 'partner.statement.wizard'
    _description = 'partner.statement.wizard'

    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date("End Date", required=True)
    partner_id = fields.Many2one('res.partner', string="Carrier", required=True)

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

        return self.env['partner.statement'].action_generate_report(self, data=data)

class PartnerStatementsReport(models.AbstractModel):
    _name = 'partner.statement'
    _description = 'partner.statement'

    def action_generate_report(self, docids, data=None):
        '''Action to generate report'''

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        partner_id = data['form']['partner_id']
        partner = data['form']['partner']

        domain = [
            ('partner_id', '=', partner_id),
            ("invoice_date", '>=', date_start),
            ("invoice_date", "<=", date_end),
            ("state", "!=", 'draft')]

        partner_ledgers = self.env["account.move"].search(domain)

        amount_total = 0.0
        total_credit = 0.0
        total_debit = 0.0
        currency_id = None

        ledgers = []

        for partner_ledger in partner_ledgers:

            move_line_query = """
                    SELECT move_name, ref, debit, credit, currency_id
                    FROM account_move_line 
                    WHERE (move_name = '%s' OR ref = '%s')
                    AND (account_internal_type='receivable' OR account_internal_type='payable')
                """%(partner_ledger.name, partner_ledger.name)

            self.env.cr.execute(move_line_query)
    
            move_records = self.env.cr.fetchall()

            for ledger in move_records:
                record = {}

                record['reference'] = ledger[0]
                record['date'] = partner_ledger.date
                record['debit'] = float(ledger[2])
                record['credit'] = float(ledger[3])
                record['currency_id'] = ledger[4]
                currency_id = ledger[4]

                if not ledger[1]:
                    record['description'] = ledger[0]
                else:
                    record['description'] = ledger[0] + ' : ' + ledger[1]

                ledgers.append(record)
            
        for line in ledgers:
            try:
                total_debit += float(line["debit"]) 
                total_credit += float(line["credit"])
            except:
                raise UserError(_(line))

        amount_total = total_credit - total_debit 

        for partner_ledger in partner_ledgers:
            currency_id = partner_ledger.currency_id.symbol
    
        docs = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'partner':partner,
            'partner_id': partner_id,
            'currency_id': currency_id,
            'order_ids':ledgers,
            'balance': float(amount_total)
        }

        return self.env.ref('quatrix_inheritance_module.partner_statement').report_action(self, data=docs, config=False)
