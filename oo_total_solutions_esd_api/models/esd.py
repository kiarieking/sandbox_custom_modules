import base64
import json
import logging
import xmltodict
from datetime import datetime
from io import BytesIO

import requests

from odoo import models
from odoo.exceptions import ValidationError
from odoo.tools import float_round
from qrcode import QRCode, constants
from requests.exceptions import Timeout, TooManyRedirects

_logger = logging.getLogger(__name__)

PATHS = {
    'settings': 'Settings',
    'status': 'ReadStatus',
    'open': 'OpenReceipt',
    'sign_out_invoice': 'OpenInvoiceWithFreeCustomerData',
    'sign_out_refund': 'OpenCreditNoteWithFreeCustomerData',
    'sell_item': 'SellPLUfromExtDB',
    'read_receipt': 'ReadCurrentReceiptInfo',
    'close': 'CloseReceipt',
    'cancel': 'CancelReceipt',
    'date': 'ReadDateTime',
    'cu_numbers': 'ReadCUnumbers',
    'inform_duplicate': 'InfoLastReceiptDuplicate'
}

ROUNDING = 0.01

DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'

SIGNED_AMOUNT_KEYS = ['SubtotalAmountVATGA', 'SubtotalAmountVATGB', 'SubtotalAmountVATGC', 'SubtotalAmountVATGD',
                      'SubtotalAmountVATGE']


def _make_signature_qrcode(url):
    qr = QRCode(version=1, box_size=25, border=6, error_correction=constants.ERROR_CORRECT_L)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    temp_img = BytesIO()
    img.save(temp_img, format='PNG')
    return base64.b64encode(temp_img.getvalue())


def _remove_non_alphanumerics(name='None'):
    return ''.join(filter(str.isalnum, name))


def _format_payload(payload):
    if not payload:
        return ''
    payload_to_str = ','.join(["{}={}".format(k, v or '') for k, v in payload.items()])
    return payload_to_str


def _retrieve_signed_invoice_data(res):
    new_res = {}
    for _r in res:
        new_res[_r.get('@Name')] = _r.get('@Value').strip()
    _logger.info('TIMS ETR: received info: {}'.format(new_res))
    return new_res


def _get_total_signed_amount(amount_group):
    amount_group = _retrieve_signed_invoice_data(amount_group)
    total = 0
    for key in SIGNED_AMOUNT_KEYS:
        total += float(amount_group.get(key, 0))
    return total


class EsdApi(models.AbstractModel):
    _name = 'oo.esd.api'
    _description = 'Tremol Esd API'

    def _error_handler(self, response, initialize=False):
        if response.status_code != 200:
            return 'TIMS ETR request failed with status code: {response.status_code}'.format(response.status_code)
        res = response.content.decode(encoding='utf-8')
        res_data = xmltodict.parse(res)
        res = json.loads(json.dumps(res_data["Res"]))

        if res.get('@Code') != '0':
            error_code = res.get('@Code')
            error_message = res.get('Err', {}).get('Message', 'Device Unreachable')
            message = 'TIMS ETR request failed with the following error code: {} and message: \n {}'.format(
                error_code, error_message)
            if not initialize:
                self.cancel_receipt()
                raise ValidationError(message)
        else:
            _logger.info(
                "TIMS ETR request successfull with the code {}: and status: {}".format(
                    res.get('@Code'), res.get('Status')))

        return res.get('Res') or res.get('Status')

    def inititalize(self, company):
        res = None
        for config in company.esd_config_ids.sorted(key=lambda s: (s.is_last_active, s.sequence), reverse=True):
            tcp = config.conn_type == "1"
            com = config.conn_type == "0"

            settings = {
                "tcp": config.conn_type or '',
                "ip": tcp and config.esd_ip or '',
                "port": tcp and config.esd_port or '',
                "password": tcp and config.esd_password or '',
                "baud": com and config.esd_baud or '',
                "com": com and config.esd_com or '',
            }
            try:
                payload = _format_payload(settings)
                server_url = config.esd_server_url

                settings_url = "{}/{}({})".format(server_url, PATHS['settings'], payload)
                status_url = "{}/{}()".format(server_url, PATHS['status'])
                _logger.info('TIMS ETR: Sending request to device {}'.format(payload))
                requests.request('GET', settings_url)
                response = requests.request('GET', status_url)

                res = self._error_handler(response, initialize=True)
                if not res:
                    continue
                _logger.info("TIMS ETR request initialized successfuly, returning response {}".format(res))

                cunumbers_url = "{}/{}()".format(server_url, PATHS['cu_numbers'])

                serial_response = requests.request('GET', cunumbers_url)
                serial_response = self._error_handler(serial_response, initialize=True)
                device_serial = _retrieve_signed_invoice_data(serial_response)
                config.write({'is_last_active': True, 'esd_device_serial': device_serial.get('SerialNumber')})
                (company.esd_config_ids - config).write({'is_last_active': False})
                return res
            except (Timeout, TooManyRedirects):
                continue
            except Exception as e:
                _logger.error('TIMS ETR: {}'.format(e))
                raise ValidationError('TIMS ETR: Device cannot be reached')
        if not res:
            raise ValidationError('TIMS ETR: Device cannot be reached')
        return res

    def call_esd(self, company, endpoint, payload=None, method='GET'):
        """
        Args:
            If multiple configurations have been set, the last successfully used config is used if available otherwise
             it tries with all other configs
            and ends if one config connects successfully or no more successful configs are there.

            company (model): the company belonging to that invoice.
            endpoint (str, optional): the path of this request as described in PATHS
            method (str, optional): can be post or get. Defaults to 'get'.
            payload (_type_, optional): For any operation requiring data to be passed through. Defaults to None.
        """
        config = company.esd_config_ids.filtered('is_last_active')
        if not config:
            raise ValidationError('TIMS ETR signature failed. Device not reachable!')

        server_url = config.esd_server_url
        url = '{}/{}({})'.format(server_url, endpoint, _format_payload(payload))

        _logger.info("TIMS ETR request made to endpoint {}".format(url))
        response = requests.request(method, url)
        res = self._error_handler(response)

        return res

    def open_receipt(self):
        endpoint = PATHS['open']
        payload = {'OptionReceiptFormat': '1', 'TraderSystemInvNum': _remove_non_alphanumerics(self.name)}
        return self.call_esd(self.company_id, endpoint, payload)

    def register_receipt(self):
        #self.open_receipt()
        partner = self.partner_id
        address = (partner.street or "") + (partner.street2 or "") + (partner.city or "")
        payload = {
            "CompanyName": _remove_non_alphanumerics(self.company_id.name)[:30],
            "ClientPINnum": partner.vat or "",
            "HeadQuarters": "",
            "Address": _remove_non_alphanumerics(address)[:30],
            "PostalCodeAndCity": "",
            "ExemptionNum": partner.tax_exemption or "",
            "TraderSystemInvNum": _remove_non_alphanumerics(self.name)
        }
        endpoint = PATHS['sign_out_invoice']
        if self.move_type == 'out_refund':
            endpoint = PATHS['sign_out_refund']
            related_invoice = self.reversed_entry_id and self.reversed_entry_id.esd_signature or ''
            payload.update({"RelatedInvoiceNum": related_invoice})
        
        _logger.info(f'TIMS sign credit note/invoice: {endpoint} payload {payload}')

        return self.call_esd(self.company_id, endpoint, payload)

    def _get_hscode_and_vat(self, line):
        hscode_id = line.hscode_id
        hscode = hsdesc = ''
        vat_tax = line.tax_ids.filtered('esd_tax_band')
        if len(vat_tax) > 1:
            vat_tax = vat_tax[0]

        if hscode_id:
            hscode, hsdesc, vat_tax = hscode_id.mapped(lambda h: (h.name, h.hsdesc, h.tax_id))[0]

        if not vat_tax:
            raise ValidationError(
                'Every line must have a tax with a valid tax band or have the product associated with a Hscode!')

        return hscode, hsdesc, vat_tax

    def _currency_convert(self, amount):
        if self.use_manual_fx:
            fx_date = self.date_invoice or datetime.today()
            if self.currency_id != self.esd_currency_id:
                amount = self.currency_id._convert(amount, self.esd_currency_id, self.company_id, fx_date, round=True,
                                                   manual_rate=self.manual_rate)
        return amount
    
    def _check_downpayment(self, lines):
        discount = 0
        down_lines = lines.filtered(lambda l: l.quantity < 0)
        _logger.info(down_lines.product_id.name)
        other_lines = lines -down_lines
        line = down_lines and down_lines[0]
        print('+++++++++++++++++ {0} --------- {1}'.format(line.price_total, sum(other_lines.mapped('price_total'))))
        # discount = line.price_total * 100 / sum(other_lines.mapped('price_total'))
        # return discount, len(other_lines)
        try:
            discount = line.price_total * 100 / sum(other_lines.mapped('price_total'))
        except ZeroDivisionError:
            discount = 0
        return discount, len(other_lines)

    def _sell_plu_from_extdb(self):
        endpoint = PATHS['sell_item']
        all_registered = True
        downpayment_discount, lines_length = self._check_downpayment(self.invoice_line_ids.filtered(lambda l: not l.display_type and l.product_id))
        _logger.info(downpayment_discount)
        for line in self.invoice_line_ids.filtered(lambda l: not l.display_type and l.product_id and l.quantity >= 0):
            discount = line.discount + downpayment_discount
            hscode, hsdesc, vat_tax = self._get_hscode_and_vat(line)
            # price_unit = line.price_unit if vat_tax.price_include else line.price_unit * 1.16
            # price_unit = line.price_unit * 1.16 if vat_tax.esd_tax_band == 'A' and not vat_tax.price_include else line.price_unit
            VAT = float_round(vat_tax.amount, precision_digits=4)/100 + 1
            price_unit = line.price_unit if vat_tax.price_include else line.price_unit * VAT
            price_unit = self._currency_convert(price_unit)
            
            payload = {
                "NamePLU": _remove_non_alphanumerics(line.name)[:36],
                "OptionVATClass": vat_tax.esd_tax_band,
                "HSCode": hscode,
                "HSName": _remove_non_alphanumerics(hsdesc)[:36],
                "MeasureUnit": _remove_non_alphanumerics(line.product_uom_id.name or line.product_id.uom_id.name)[:36],
                "Price": float_round(price_unit, precision_digits=4),
                "Quantity": float_round(line.quantity, precision_digits=4),
                "VATGrRate": float_round(vat_tax.amount, precision_digits=4),
                "DiscAddP": float_round(abs(discount), precision_digits=4) * -1 or ''
            }
            
            response = self.call_esd(self.company_id, endpoint, payload)
            if response:
                line.is_esd_signed = True
            all_registered = all_registered and response
        return all_registered

    def inform_duplicate(self):
        endpoint = PATHS['inform_duplicate']
        return self.call_esd(self.company_id, endpoint)

    def read_receipt_information(self):
        endpoint = PATHS['read_receipt']
        return self.call_esd(self.company_id, endpoint)

    def close_receipt(self):
        endpoint = PATHS['close']
        return self.call_esd(self.company_id, endpoint)

    def cancel_receipt(self):
        try:
            endpoint = PATHS['cancel']
            config = self.company_id.esd_config_ids.filtered('is_last_active')
            if not config:
                raise ValidationError('TIMS ETR signature failed. Device not reachable!')

            server_url = config.esd_server_url
            url = '{}/{}({})'.format(server_url, endpoint, _format_payload(None))

            _logger.info("TIMS ETR request made to endpoint {} ...with payload: {}".format(endpoint, None))
            
            requests.request('GET', url)
        except Exception as e:
            _logger.error(e)
        return True

    def _read_receipt_date(self):
        endpoint = PATHS['date']
        return self.call_esd(self.company_id, endpoint)

    def _read_cu_numbers(self):
        endpoint = PATHS['cu_numbers']
        return self.call_esd(self.company_id, endpoint)

    def _sign_invoice(self):
        status = self.inititalize(self.company_id)
        if status:
            status = self.register_receipt()
            all_registered = self._sell_plu_from_extdb()
            if all_registered:
                receipt_info_res = self.read_receipt_information()
                sign_response = self.close_receipt()
                if self.esd_signature:
                    self.inform_duplicate()

                date_response = self._read_receipt_date()
                serial_response = self._read_cu_numbers()

                response_signature = _retrieve_signed_invoice_data(sign_response)
                date_signed = datetime.strptime(date_response.get('@Value'), DATETIME_FORMAT)
                device_serial = _retrieve_signed_invoice_data(serial_response)
                esd_total_signed = _get_total_signed_amount(receipt_info_res)

                self.write({
                    'esd_date_signed': date_signed,
                    'esd_device_serial': device_serial.get('SerialNumber'),
                    'esd_total_signed': esd_total_signed,
                    'esd_signature': response_signature.get('InvoiceNum'),
                    'esd_qr_code': _make_signature_qrcode(response_signature.get('QRcode'))
                })
                _logger.info("TIMS ETR request --> successfuly signed invoice: {}".format(self.name))

                self.sudo().message_post(
                    body="Invoice Successfuly Signed. Invoice Signature --> {}".format(response_signature.get('InvoiceNum')))
        return True
