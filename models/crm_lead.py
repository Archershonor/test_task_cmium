from odoo import api, models, fields


class Lead(models.Model):
    _inherit = 'crm.lead'

    operator_id = fields.Many2one(comodel_name='res.partner',
                                  check_company=True, string='Operator')

    delivery_partner_id = fields.Many2one(comodel_name='res.partner',
                                   string='Delivery partner',
                                   check_company=True,
                                   domain=[('iam_delivery_partner', '=', True)])

    lead_source = fields.Selection([('advertising', 'Advertasing'),
                                    ('recommendation', 'Recommendation')],
                                   required=True)

    communication_channel = fields.Selection([('email', 'E-mail'),
                                              ('phone', 'Phone'),
                                              ('telegram', 'Telegram'), ],
                                             required=True)

    paid_sum = fields.Monetary(currency_field='company_currency', compute='_compute_paid_sum')

    orders_sum = fields.Monetary(currency_field='company_currency', compute='_compute_orders_sum')

    payment_progress = fields.Float(compute='_compute_payment_progress')

    @api.depends('order_ids', 'order_ids.amount_total')
    def _compute_paid_sum(self):
        for lead in self:
            lead.paid_sum = sum(lead.order_ids.mapped('paid_invoices_amount'))

    @api.depends('order_ids', 'order_ids.amount_total')
    def _compute_orders_sum(self):
        for lead in self:
            lead.orders_sum = sum(lead.order_ids.mapped('amount_total'))

    @api.depends('order_ids', 'order_ids.amount_total')
    def _compute_payment_progress(self):
        for rec in self:
            if rec.orders_sum:
                rec.payment_progress = 100 * rec.paid_sum / rec.orders_sum
            else:
                rec.payment_progress = 0

    def action_show_relates_orders(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale order',
            'res_model': 'sale.order',
            'domain': [('opportunity_id', '=', self.id)],
            'view_mode': 'tree',
            'target': 'current'
        }
