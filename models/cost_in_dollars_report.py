from odoo import api, fields, models


class CostinDollarsReport(models.TransientModel):
    _name = 'cost.in.dollars.report'

    lines = fields.One2many(
        comodel_name='cost.dlls.report.line',
        inverse_name='report',
    )

    @api.one
    def create_report(self):
        landed_costs = self.env['stock.landed.cost'].search([('name', '=', 'LC/2017/0005')]).sorted(key=lambda r: r.date)  # TODO Only done?
        products = self.env['product.product'].search([])
        for product in products:
            for landed_cost in landed_costs:
                for valuation_adjustment_line in landed_cost.valuation_adjustment_lines:
                    if product == valuation_adjustment_line.product_id:
                        line = self.env['cost.dlls.report.line'].search([('report', '=', self.id), ('product', '=', product.id)])
                        if not line:
                            line_dict = {
                                'product': product.id,
                                'landed_cost': landed_cost.id,
                                'landed_cost_quantity': valuation_adjustment_line.quantity,
                                'landed_cost_former_cost': valuation_adjustment_line.former_cost,
                            }
                            line = self.env['cost.dlls.report.line'].create(line_dict)
                            line.report = self
                        line.valuation_adjustment_lines += valuation_adjustment_line
