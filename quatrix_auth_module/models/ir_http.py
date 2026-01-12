# -*- coding: utf-8 -*-

import logging

from odoo.http import request
from odoo import models, _
from odoo.exceptions import AccessDenied, UserError


_logger = logging.getLogger(__name__)


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    @classmethod
    def _auth_method_api_key(cls):
        headers = request.httprequest.environ
        api_key = headers.get('HTTP_X_API_KEY')

        if api_key:
            request.uid = 1
            auth_api_key = request.env['auth.api.key'].search([('key', '=', api_key)])
            if auth_api_key:
                request._env = None
                request.uid = auth_api_key.user_id.id
                request.auth_api_key = auth_api_key
                return True
        
        _logger.error("Wrong HTTP_API_KEY, access denied %s"%str(headers.keys()))

        raise AccessDenied()
