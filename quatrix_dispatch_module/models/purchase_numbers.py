# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import fields, models, api, _
from odoo.exceptions import UserError

class PurchaseNumber(models.Model):
    _name = 'purchase.number'    
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = "Purchase Numbers"
    _order = "end_date desc"

    name = fields.Char(string="PO Number", required=True)
    name_seq = fields.Char(string='Purchase Number', required=True,
        copy=False, readonly=True, index=True, default=lambda self: _('New'))
    start_date = fields.Date(string="Start Date", required=True, default = lambda self: fields.datetime.now())
    end_date = fields.Date(string="End Date", required=True)
    purchase_ids = fields.One2many('purchase.number.line', 'purchase_id')
    amount_total = fields.Float(compute="_compute_total_amount")
    potype = fields.Selection([('MOPUP', "MOPUP"), ('BEER', 'BEER'),
        ('DEFCO', 'DEFCO'), ('KEG', 'KEG'), ('UDV', 'UDV'), ('CGI', 'CGI'), ('HOUSEKEEPING', 'HOUSEKEEPING'), ('PARTYCENTRAL', 'PARTYCENTRAL'), ('BDC', 'BDC TRANSFER'), ('EAML', 'EAML'), ('FUEL SURCHARGE', 'FUEL SURCHARGE')], default='MOPUP', string="PO Type")
    currency_id = fields.Many2one('res.currency', 'Currency', compute='_compute_currency_id')
    user_id = fields.Many2one('res.users', compute="_get_current_user", string='Staff',
        ondelete="restrict", default=lambda self: self.env.user)
    partner_id = fields.Many2one('res.partner', string="Customer",
        required=True, change_default=True, index=True, tracking=True)
    partner_invoice_id = fields.Many2one(
        'res.partner', string='Invoice Address',
        readonly=True,
        states={'draft': [('readonly', False)],
            'order': [('readonly', False)], 'posted': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    partner_shipping_id = fields.Many2one(
        'res.partner', string='Delivery Address', readonly=True,
        states={'draft': [('readonly', False)],
            'order': [('readonly', False)], 'posted': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",)
    company_id = fields.Many2one('res.company', 'Company',
        required=True, index=True, default=lambda self: self.env.company)
    
    status = fields.Selection(
        [('draft', "Quotation"),('order', "LPO Order"), ('expired', "Expired"), ('cancel', "Cancelled")], default='draft')

    @api.depends('purchase_ids.amount_subtotal')
    def _compute_total_amount(self):
        '''Calculate total amount from lines'''

        for record in self:
            amount_total = 0.0
            for line in record.purchase_ids:
                amount_total += line.amount_subtotal
            record.update({'amount_total': amount_total })

    @api.model
    def create(self, vals):
        '''Create a purchase number record and create a new sequence number'''

        if vals.get('name_seq', _('New')) == _('New'):
            vals['name_seq'] = self.env['ir.sequence'].next_by_code('local.purchase.document') or _('New')
        result =super(PurchaseNumber, self).create(vals)
        return result

    @api.depends()
    def _compute_currency_id(self):
        '''Return active company currency, expected KSH'''

        for record in self:
            record.currency_id = self.env.user.company_id.sudo().currency_id.id

    @api.depends()
    def _get_current_user(self):
        '''Return the active user'''

        self.update({'user_id' : self.env.user.id})

    @api.depends('purchase_ids.quantity', 'purchase_ids.remaining_quantity', 'end_date')
    def _check_expired_documents(self):
        '''Check if LPO is exhausted or expired'''

        remaining_trips_list = []

        for record in self:
            if record.end_date > datetime.now():
                record.update({'status': 'expired'})

            for line in record.purchase_ids:
                remaining_trips_list.append(line.remaining_quantity)
            
            if sum(remaining_trips_list) == 0:
                record.update({'status': 'expired'})

    def action_cancel(self):
        '''button function to cancel a PO Document'''

        trips_completed = []

        for record in self:
            for line in record.purchase_ids:
                trips_completed.append(line.trips_completed)
            if sum(trips_completed) > 0:
                raise UserError(_('You cannot cancel a PO that has completed trips'))
            else:
                record.update({'status': 'cancel'})

    def action_confirm(self):
        '''Button function to confirm an LPO Document'''

        for record in self:
            record.update({'status': 'order'})

    def action_reset(self):
        '''Button to reset a cancelled order back to draft by updating the status'''

        for record in self:
            record.update({'status': 'draft'})
    
    def action_update_dispatch_records(self):
        '''Find all dispatch records without a PO and populate them if a PO product exists.'''

        dispatch_records = self.env['purchase.dispatch'].search([('purchase_id', '=', False), ('status', '=', 'order')])

        if not dispatch_records:
            raise UserError(_("All records have been synchronized!"))
        
        #TODO: Refactor function to have a more efficient time complexity

        for record in self:
            for dispatch_record in dispatch_records:
                for line in record.purchase_ids:
                    for dispatch_line in dispatch_record.order_ids:
                        if line.remaining_quantity != 0:
                            if (line.product_id == dispatch_line.product_id or line.optional_product_id == dispatch_line.product_id) and dispatch_record.pod_link is not None:
                                dispatch_record.update({'purchase_id': record.id})
                                dispatch_record.sudo().action_post()




                        
                        # Alternative for the above if statement -----> This will however stop the loop when a remaining quantity in a line is 0
                        # Therefore the rest of the lines will not be processed.

                        # if line.remaining_quantity == 0:
                        #     return

                        # if (line.product_id == dispatch_line.product_id or line.optional_product_id == dispatch_line.product_id) and dispatch_record.pod_link is not None:
                        #     dispatch_record.update({'purchase_id': record.id})
                        #     dispatch_record.sudo().action_post()


