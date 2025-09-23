from odoo import api, models, fields, _ 
from odoo.exceptions import UserError
from datetime import datetime, timedelta
import json

class TonnageDispatchWizard(models.TransientModel):
    _name = 'tonnage.report.wizard'
    _description = 'tonnage.report.wizard'

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

        return self.env['tonnage.revenue.report'].action_generate_report(self, data=data)

class TonnageDispatchReport(models.AbstractModel):
    _name = 'tonnage.revenue.report'
    _description = 'tonnage.revenue.report'

    def action_generate_report(self, docids, data=None):
        '''Action to generate report'''
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']

        if (not date_start) or (not date_end):
            raise UserError("Enter start and end date!")

        start = (date_start).strftime("%Y-%m-%d %H:%M:%S")
        end = (date_end + timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
        
        tables = ['quatrix', 'purchase']
        records = list()

        for table in tables:
            query = f'''SELECT {table}_dispatch.partner_id AS partner_id,
                            res_partner.name as partner_name,
                            SUM({table}_dispatch_line.carrier_price) as carrier_charges,
                            SUM({table}_dispatch_line.quantity * {table}_dispatch_line.price_unit) as amount_total,
                            fleet_vehicle.vehicle_size AS vehicle_size
                        FROM {table}_dispatch, fleet_vehicle, res_partner, {table}_dispatch_line
                        WHERE res_partner.id = partner_id
                        AND {table}_dispatch.vehicle_id = fleet_vehicle.id
                        AND  date_dispatch >= '{start}'
                        AND date_dispatch <= '{end}'
                        AND {table}_dispatch.id = {table}_dispatch_line.order_id
                        GROUP BY vehicle_size, partner_id, partner_name
                    '''

            self.env.cr.execute(query)
            table_name = table+'_data'
            table_name = self.env.cr.dictfetchall()

            for dic in table_name:
                records.append(dic)
        
        sorted_records = []
        headers = set()

        for record in records:
           
            margin = record['amount_total'] - record['carrier_charges']
            margin_percentage = 0

            if record['amount_total'] > 0:
                margin_percentage = (margin/record['amount_total']) * 100
            
            d = {
                # 'partner_name': record['partner_name'],
                record['partner_name']: {
                    'partner_name': record['partner_name'],
                    'MC':0,
                    '1.5T': 0,
                    '3T': 0,
                    '5T': 0,
                    '7T': 0,
                    '10T': 0,
                    '14T': 0,
                    '28T': 0,
                    'other':0,
                    'total': 0,
                    }}

            if record['partner_name'] in d:
                if record['vehicle_size'] == 'motorcycle' or record['vehicle_size'] == 'MotorCycle':
                    d[record['partner_name']]['MC'] += record['amount_total']

                elif record['vehicle_size'] == '1.5T':
                    d[record['partner_name']]['1.5T'] += record['amount_total']

                elif record['vehicle_size'] == '3T':
                    d[record['partner_name']]['3T'] += record['amount_total']

                elif record['vehicle_size'] == '5T':
                    d[record['partner_name']]['5T'] += record['amount_total']

                elif record['vehicle_size'] == '7T':
                    d[record['partner_name']]['7T'] += record['amount_total']

                elif record['vehicle_size'] == '10T':
                    d[record['partner_name']]['10T'] += record['amount_total']

                elif record['vehicle_size'] == '14T':
                    d[record['partner_name']]['14T'] += record['amount_total']

                elif record['vehicle_size'] == '28T':
                    d[record['partner_name']]['28T'] += record['amount_total']
                else:
                    d[record['partner_name']]['other'] += record['amount_total']

            sorted_records.append(d)
        
        # Merge Records
        merged_records = []
        merged = {}
        
        for item in sorted_records:
            
            for key in item.keys():
                if key not in merged:
                    merged[key] = {}

                for k, v in item[key].items():
                    if k not in merged[key]:
                        merged[key][k] = v
                    else:
                        if v > merged[key][k]: merged[key][k] = v
        for key, value in merged.items():
            merged_records.append(value)
        
        # Calculate totals per client
        for item in merged_records:
            for key, value in item.items():
                if key != 'partner_name' and key != 'total':
                    item['total'] += value
        
        # Calculate total revenue
        total_revenue = 0
        for item in merged_records:
            total_revenue += item['total']

        sorted_list = sorted(merged_records, reverse=True, key = lambda i: (i['total'], i['partner_name']))

        docs = {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'date_start': date_start,
            'date_end': date_end,
            'total_revenue':total_revenue,
            'order_ids': sorted_list
        }


        return self.env.ref('quatrix_dispatch_module.tonnage_revenue_report').report_action(self, data=docs, config=False)

