from odoo import api, fields, models


class Apportionment(models.Model):
    _name = 'cost.dlls.report.line.apportionment'

    line = fields.Many2one(
        comodel_name='cost.dlls.report.line',
    )
    product = fields.Many2one(
        comodel_name='product.product'
    )
    additional_landed_cost = fields.Float(
        default=0,
    )


class LineReport(models.TransientModel):
    _name = 'cost.dlls.report.line'

    apportionments = fields.One2many(
        comodel_name='cost.dlls.report.line.apportionment',
        inverse_name='line',
    )
    report = fields.Many2one(
        comodel_name='cost.in.dollars.report',
    )
    product = fields.Many2one(
        comodel_name='product.product',
    )
    product_default_code = fields.Char(
        related='product.default_code',
    )
    product_name = fields.Char(
        related='product.name',
    )
    landed_cost_quantity = fields.Float()
    landed_cost_former_cost = fields.Float()
    landed_cost_date = fields.Date(
        related='landed_cost.date',
    )
    landed_cost = fields.Many2one(
        comodel_name='stock.landed.cost',
    )
    valuation_adjustment_lines = fields.Many2many(
        comodel_name='stock.valuation.adjustment.lines',
    )
    currency_rate = fields.Many2one(
        comodel_name='res.currency.rate',
        compute='_get_currency_rate'
    )
    inverse_currency_rate = fields.Float(
        compute='_get_inverse_currency_rate',
    )
    total_cost = fields.Float(
        compute='_get_total_cost',
        digits=(9, 2),
    )
    unit_cost = fields.Float(
        compute='_get_unit_cost',
        digits=(9, 2),
    )
    unit_cost_usd = fields.Float(
        compute='_get_unit_cost_usd',
        digits=(9, 2),
    )

    @api.one
    @api.depends('landed_cost_date')
    def _get_currency_rate(self):
        if self.landed_cost_date:
            self.currency_rate = self.env['res.currency.rate'].search([('name', '<=', self.landed_cost_date)]).sorted(key=lambda r: r.name)[-1]

    @api.one
    @api.depends('currency_rate')
    def _get_inverse_currency_rate(self):
        if self.currency_rate.rate:
            self.inverse_currency_rate = 1/self.currency_rate.rate

    @api.one
    @api.depends('landed_cost_former_cost', 'valuation_adjustment_lines')
    def _get_total_cost(self):
        self.total_cost = self.landed_cost_former_cost
        for l in self.valuation_adjustment_lines:
            self.total_cost += l.additional_landed_cost

    @api.one
    @api.depends('total_cost', 'landed_cost_quantity')
    def _get_unit_cost(self):
        if self.landed_cost_quantity:
            self.unit_cost = self.total_cost/self.landed_cost_quantity

    @api.one
    @api.depends('unit_cost', 'currency_rate')
    def _get_unit_cost_usd(self):
        self.unit_cost_usd = self.unit_cost*self.currency_rate.rate
