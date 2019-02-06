# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from base64 import b64decode, b64encode
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.depends('origin')
    def _compute_related_sale_order(self):
        for invoice in self:
            origin = invoice.origin and invoice.origin.split(',')
            if origin and len(origin):
                sale_order = self.env['sale.order'].search([('name','=',origin[0])], limit=1)
                invoice.payment_type = sale_order.payment_type if sale_order else False
                invoice.warehouse_id = sale_order.warehouse_id if sale_order else False
                invoice.amount_calculate_cost = sale_order.amount_calculate_cost if sale_order else 0.0

    payment_type = fields.Char(
        'Es Credito', compute='_compute_related_sale_order', store=True)
    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse', compute='_compute_related_sale_order', store=True)
    amount_calculate_cost = fields.Monetary(string='Costo', compute='_compute_related_sale_order', store=True)
    fiscal_printer_status = fields.Selection([
            ('unsent','Sin enviar'),
            ('sent','Enviada'),
            ('printed','Impresa'),
        ], 'Impresora Fiscal', readonly=True, default=lambda *a: 'unsent')

    @api.multi
    def send_invoice_proxy(self):
        self.ensure_one()
        cmd = "jR%s"%(self.partner_id.vat,)
        cmd += "\njS%s"%(self.partner_id.name,)
        cmd += "\nj%s"%(self.partner_id.street,) if self.partner_id.street else ''
        for line in self.invoice_line_ids:
            if line.invoice_line_tax_ids:
                tmp = '\n!{:011.2f}{:09.3f}{}'.format(line.price_unit, line.quantity, line.name.replace('\n','')[:117])
                cmd += tmp.replace('.','')
            else:
                tmp = '\n {:011.2f}{:09.3f}{}'.format(line.price_unit, line.quantity, line.name.replace('\n','')[:117])
                cmd += tmp.replace('.','')
        cmd += "\n3\n101"
        cmd = b64encode(cmd.encode('utf-8'))
        self.fiscal_printer_status = 'sent'
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': 'http://127.0.0.1:8080/sendcmd/%s'%(cmd.decode("utf-8"),),
        }
