from odoo import api, fields, models


class CostinDollarsReport(models.TransientModel):
    _name = 'cost.in.dollars.report'

    lines = fields.One2many(
        comodel_name='cost.dlls.report.line',
        inverse_name='report',
    )
    apportionments = fields.Many2many(
        comodel_name='product.product'
    )

    @api.one
    def create_report(self):
        landed_costs = self.env['stock.landed.cost'].search([('state', '=', 'done')]).sorted(key=lambda r: r.date)  # TODO Only done?
        products = self.env['product.product'].search([])
        for product in products:
            new_product = False
            for landed_cost in landed_costs:
                for valuation_adjustment_line in landed_cost.valuation_adjustment_lines:
                    if new_product:
                        continue
                    if product == valuation_adjustment_line.product_id:
                        line = self.env['cost.dlls.report.line'].search([('report', '=', self.id), ('product', '=', product.id)])
                        if not line:
                            new_product = True
                            line_dict = {
                                'product': product.id,
                                'landed_cost': landed_cost.id,
                                'landed_cost_quantity': valuation_adjustment_line.quantity,
                                'landed_cost_former_cost': valuation_adjustment_line.former_cost,
                            }
                            line = self.env['cost.dlls.report.line'].create(line_dict)
                            line.report = self
                            self.lines |= line
                        self.apportionments |= valuation_adjustment_line.cost_line_id.product_id
                        line.valuation_adjustment_lines |= valuation_adjustment_line
                        self.env['cost.dlls.report.line.apportionment'].create({
                            'product': valuation_adjustment_line.cost_line_id.product_id.id,
                            'additional_landed_cost': valuation_adjustment_line.additional_landed_cost,
                        }).line = line
        for apportionment in self.apportionments:
            for line in self.lines:
                if apportionment not in [a.product for a in line.apportionments]:
                    self.env['cost.dlls.report.line.apportionment'].create({
                        'product': apportionment.id,
                    }).line = line
        self.apportionments = self.apportionments.sorted(key=lambda r: r.name)
        for line in self.lines:
            line.apportionments = line.apportionments.sorted(key=lambda r: r.product.name)
