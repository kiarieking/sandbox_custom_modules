import logging

from odoo import api, models, fields, _ 
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
class SaleUninvoicedReportWizard(models.TransientModel):
    _name = 'sale.uninvoiced.report.wizard'
    _description = 'sale.uninvoiced.report.wizard'

    date_start = fields.Date('Start Date', required=False)
    date_end = fields.Date("End Date", required=False)

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

        return self.env['sale.uninvoiced.report'].action_generate_report(self, data=data)

class SaleUninvoicedReport(models.AbstractModel):
    _name = 'sale.uninvoiced.report'
    _description = 'sale.uninvoiced.report'

    def action_generate_report(self, docids, data=None):
        '''Action to generate report'''

        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        if date_start and not date_end:
            raise UserError("Please enter the end date")

        if date_end and not date_start:
            raise UserError("Please enter the start date")

        domain = [("invoice_status", "!=", 'invoiced')]

        if date_start and date_end:
            domain = [
                ("date_order", '>=', date_start),
                ("date_order", "<=", date_end),
                ("invoice_status", "!=", 'invoiced')]
        total_sales = 0
        sale_docs = self.env['sale.order'].search_read(domain)

        for sale_doc in sale_docs:
            total_sales += sale_doc['amount_total']

        docs = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'order_ids':sale_docs,
            'total_sales': total_sales
        }
  
        return self.env.ref('quatrix_inheritance_module.sale_uninvoiced_report').report_action(self, data=docs, config=False)