import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    tax_exemption = fields.Char(string='KRA Tax Exemption', help="Insert Tax Exemption Certificate Number")


class ResCompany(models.Model):
    _inherit = 'res.company'

    esd_enable = fields.Boolean(string='Enable ESD', help="Enable Invoices Signing")
    esd_config_ids = fields.One2many('res.esd.config', inverse_name='company_id', string='ESD Configs')

    def check_device_connection(self):
        self.ensure_one()
        _logger.info('Device connection for company {} requested by {}'.format(self.name, self.env.user.name))
        notification = {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
        response = self.env['oo.esd.api'].inititalize(company=self)
        if not response:
            notification['params'].update({
                'message': 'Device not reachable or not readable!',
                'type': 'danger',
            })
        return notification


class ResEsdConfig(models.Model):
    _name = 'res.esd.config'
    _description = 'Tremol ESD Config'
    _order = 'sequence asc'

    company_id = fields.Many2one('res.company', string='Company')
    sequence = fields.Integer(string='Sequence')
    conn_type = fields.Selection(string='Connection Type', selection=[('0', 'BAUD'), ('1', 'TCP')], required=True)
    esd_server_url = fields.Char(string='Server Url', required=True,
                                 help="A valid Url to the server the device is installed on.")
    esd_password = fields.Char(string='Password')
    esd_device_serial = fields.Char(string='Device Serial')
    esd_com = fields.Char(string='Comport Number')
    esd_baud = fields.Char(string='Comport Speed')

    esd_ip = fields.Char(string='Esd IP', help="The ip allocated to the esd device")
    esd_port = fields.Integer(string='Port', help="Open port on your ESD device")
    is_last_active = fields.Boolean('Last Active', readonly=True)


class ResCurrency(models.Model):
    _inherit = 'res.currency'

    def _convert(self, from_amount, to_currency, company, date, round=True, manual_rate=False):
        """Returns the converted amount of ``from_amount``` from the currency
        ``self`` to the currency ``to_currency`` for the given ``date`` and
        company.
        :param company: The company from which we retrieve the convertion rate
        :param date: The nearest date from which we retriev the conversion rate.
        :param round: Round the result or not
        """

        self, to_currency = self or to_currency, to_currency or self
        assert self, "convert amount from unknown currency"
        assert to_currency, "convert amount to unknown currency"
        assert company, "convert amount from unknown company"
        assert date, "convert amount from unknown date"

        # apply conversion rate
        if self == to_currency:
            to_amount = from_amount
        else:
            to_amount = from_amount * \
                        self._get_conversion_rate(self, to_currency, company, date)
            if manual_rate:
                to_amount = from_amount * manual_rate
        # apply rounding
        return to_currency.round(to_amount) if round else to_amount
