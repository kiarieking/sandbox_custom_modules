from odoo import models, api, _, fields


class FleetVehicleLog(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    
    liter = fields.Float()
    price_per_liter = fields.Float()