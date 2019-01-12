# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.depends('payment_term_id')
    def _compute_payment_type(self):
        for sale in self:
            pt = sale.payment_term_id
            sale.payment_type =  'Contado' if (not pt or pt.id == 1) else 'Credito'

    payment_type = fields.Char(
        'Es Credito', compute='_compute_payment_type', store=True)


class SaleDailyReport(models.TransientModel):
    _name = 'sale.daily.report'
    _description = 'Sale Daily Report'

    compute_at_date = fields.Selection([
        (0, 'Al dia'),
        (1, 'A una Fecha')
    ], string="Reporte", help="Reporte de hoy o de una determinada fecha")
    date = fields.Date('Fecha de reporte', help="Fecha para el reporte de ventas", default=fields.Datetime.now)

    def open_report(self):
        data = {}
        data['form'] = self.read(['compute_at_date', 'date'])[0]
        return self.env.ref('sale_premiumpaint.action_report_saledaily').report_action(self, data=data)


class SaleDailyReport(models.AbstractModel):

    _name = 'report.sale_premiumpaint.report_saledaily'

    @api.multi
    def get_report_values(self, docids, data=None):
        data = dict(data or {})
        if not data.get('date', False):
            data['date'] = fields.Date.context_today(self)
        domain = [('confirmation_date','>=', data['date'] + " 00:00:00"),('confirmation_date','<=', data['date'] + " 23:59:59"),('state','in',('sale','done'))]
        docs = self.env['sale.order'].browse(docids)
        sale_data = self.env['sale.order'].read_group(domain,fields=['warehouse_id','amount_total'], groupby=['warehouse_id'])
        for sd in sale_data:
            sd['Contado'] = sd['Credito'] =0.0
            if '__domain' in sd:
                sale_payment_type = self.env['sale.order'].read_group(sd['__domain'],fields=['payment_type','amount_total'], groupby=['payment_type'])
                for spt in sale_payment_type:
                    sd[spt['payment_type']] = spt['amount_total']
        return {
            'doc_ids': docs.ids,
            'doc_model': 'sale.order',
            'docs': docs,
            'data': sale_data,
            'date_at': data['date'],
        }
        return data
