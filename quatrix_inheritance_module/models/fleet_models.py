# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class Fleet(models.Model):
    _inherit='fleet.vehicle'

    carrier_id = fields.Many2one('res.partner', string="Carrier/Subcontractor", readonly=False, compute="_populate_carrier")
    driver_id = fields.Many2one('res.partner', string="Driver", readonly=False, compute="_populate_driver")
    carrier_driver_id = fields.Char('Driver ID', readonly=False)
    carrier_carrier_id = fields.Char("Carrier ID", readonly=False)
    carrier_vehicle_id = fields.Char("Vehicle ID", readonly=False)
    vehicle_size = fields.Char("Vehicle Size")

    _sql_constraints = [
                ('license_plate_unique', 
                'unique(license_plate)',
                'Enter another value - License plate has to be unique!')
    ]

    @api.depends('carrier_carrier_id')
    def _populate_carrier(self):
        '''Populate carrier_id based on carrier_carrier_id'''

        for record in self:
            carriers = self.env['res.partner'].search([('carrier_carrier_id', '=', record.carrier_carrier_id)])

            if carriers is not None:
                for carrier in carriers:
                    record.write({ 'carrier_id': carrier.id})
            else:
                raise UserError('The selected User does not exist!')

    @api.depends('carrier_driver_id')
    def _populate_driver(self):
        '''Populate driver_id based on carrier_carrier_id'''

        for record in self:
            carriers = self.env['res.partner'].search([('carrier_carrier_id', '=', record.carrier_driver_id)])

            if carriers is not None:
                for carrier in carriers:
                    record.driver_id = carrier.id
            else:
                raise UserError('The selected User does not exist!')

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        '''Update search filter: Filter using licence plates instead of name'''
        args = args or []
        recs = self.browse()

        if not recs:
            recs = self.search([('license_plate', operator, name)] + args, limit=limit)
        return recs.name_get()