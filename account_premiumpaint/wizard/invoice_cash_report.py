# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class InvoiceDailyReport(models.TransientModel):
    _name = 'invoice.cash.report'
    _description = 'Invoice Cash Report'

    compute_at_date = fields.Selection([
        (0, 'Al dia'),
        (1, 'A una Fecha')
    ], string="Reporte", help="Reporte del dia o de una determinada fecha")
    date = fields.Date('Fecha de reporte', help="Fecha para el reporte de Caja", default=fields.Date.context_today)
    warehouse_id = fields.Many2one('stock.warehouse', 'Sucursal', required=True)

    def open_report(self):
        data = {}
        data['form'] = self.read(['compute_at_date', 'date', 'warehouse_id'])[0]
        return self.env.ref('account_premiumpaint.action_report_invoicecash').report_action(self, data=data)
