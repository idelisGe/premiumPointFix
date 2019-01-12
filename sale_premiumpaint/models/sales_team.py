# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def _default_warehouse_id(self):
        team = self.env['crm.team']._get_default_team_id()
        warehouse_ids = super(SaleOrder, self)._default_warehouse_id()
        return team.warehouse_id if (team and team.warehouse_id) else warehouse_ids

    warehouse_id = fields.Many2one(
        'stock.warehouse', string='Warehouse',
        required=True, readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        default=_default_warehouse_id)


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
 