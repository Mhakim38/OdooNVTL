from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)

class HrExpense(models.Model):
    _inherit = 'hr.expense'

    product_id = fields.Many2one('product.product', string='Month', required=False)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=False)

    commission_line_ids = fields.One2many(
        'expense.commission.line',
        'expense_id',
        string="Invoice Breakdown"
    )

    total_invoice = fields.Float(
        string="Total Invoice Amount",
        compute="_compute_total_invoice",
        store=True
    )

    @api.depends('commission_line_ids.invoice_total')
    def _compute_total_invoice(self):
        for rec in self:
            rec.total_invoice = sum(rec.commission_line_ids.mapped('invoice_total'))

    name = fields.Char(string='Month',store=True)

    commission_attachment_ids = fields.Many2many(
        'ir.attachment',
        'hr_expense_commission_attachment_rel',
        'expense_id',
        'attachment_id',
        string='Invoices',
        domain="[('res_model', '=', 'hr.expense')]"
    )

    new_customer_attachment_ids = fields.Many2many(
        'ir.attachment',
        'hr_expense_new_customer_attachment_rel',
        'expense_id',
        'attachment_id',
        string='Invoices',
        domain="[('res_model', '=', 'hr.expense')]"
    )

    toll_attachment_ids = fields.Many2many(
        'ir.attachment',
        'hr_expense_toll_attachment_rel',
        'expense_id',
        'attachment_id',
        string='Receipts',
        domain="[('res_model', '=', 'hr.expense')]"
    )
    # Outstation Toll Claim control
    outstation_toll = fields.Boolean(string="Outstation Toll Claim")
    outstation_toll_line_ids = fields.One2many(
        'expense.outstation.toll.line',
        'expense_id',
        string="Outstation Toll Lines"
    )

    entertainment_attachment_ids = fields.Many2many(
        'ir.attachment',
        'hr_expense_entertainment_attachment_rel',
        'expense_id',
        'attachment_id',
        string='Receipts',
        domain="[('res_model', '=', 'hr.expense')]"
    )

    petrol_attachment_ids = fields.Many2many(
        'ir.attachment',
        'hr_expense_petrol_attachment_rel',
        'expense_id',
        'attachment_id',
        string='Receipts',
        domain="[('res_model', '=', 'hr.expense')]"
    )

    accommodation_attachment_ids = fields.Many2many(
        'ir.attachment',
        'hr_expense_accommodation_attachment_rel',
        'expense_id',
        'attachment_id',
        string='Hotel Receipts',
        domain="[('res_model', '=', 'hr.expense')]"
    )

    car_allowance_attachment_ids = fields.Many2many(
        'ir.attachment',
        'hr_expense_car_allowance_attachment_rel',
        'expense_id',
        'attachment_id',
        string='Receipts',
        domain="[('res_model', '=', 'hr.expense')]"
    )

    gross_profit = fields.Float(string="Gross Profit (GP)")

    sales_type = fields.Selection([
        ('indoor', 'Indoor Sales Team'),
        ('outdoor', 'Outdoor Sales Team'),
    ], string="Sales Type")

    customer_type = fields.Selection([
        ('new', 'New'),
        ('own', 'Own'),
        ('company', 'Company'),
        ('transfer', 'Transfer'),
    ], string="Customer Type")

    new_customer_ids = fields.One2many(
        'expense.new.customer.line',
        'expense_id',
        string="New Customers"
    )

    commission = fields.Monetary(string="Commission", compute="_compute_claims", store=True)

    new_customer_incentive = fields.Monetary(string="New Customer Incentive", compute="_compute_claims", store=True)

    entertainment_claimed = fields.Monetary(string="Entertainment Claimed")

    entertainment_claim = fields.Monetary(
        string="Entertainment Claims",
        compute="_compute_entertainment_claim",
        currency_field='currency_id',
        store=True
    )

    entertainment_max_claim = fields.Monetary(
        string="Max Claim Amount",
        compute="_compute_entertainment_max_claim",
        currency_field='currency_id',
        store=True
    )

    @api.depends('total_gross_sales', 'sales_type')
    def _compute_entertainment_max_claim(self):
        for rec in self:
            if rec.sales_type != 'outdoor':
                rec.entertainment_max_claim = 0.0
            elif rec.total_gross_sales <= 9999:
                rec.entertainment_max_claim = 400
            elif rec.total_gross_sales <= 50000:
                rec.entertainment_max_claim = 500
            elif rec.total_gross_sales <= 100000:
                rec.entertainment_max_claim = 1000
            else:
                rec.entertainment_max_claim = 2000

    entertainment_line_ids = fields.One2many(
        'expense.entertainment.line',
        'expense_id',
        string="Entertainment Claims"
    )

    @api.depends('total_gross_sales', 'sales_type', 'entertainment_line_ids.amount')
    def _compute_entertainment_claim(self):
        for rec in self:
            total = sum(line.amount for line in rec.entertainment_line_ids)

            if rec.sales_type != 'outdoor':
                rec.entertainment_claim = 0.0
            else:
                cap = 0.0
                if rec.total_gross_sales <= 9999:
                    cap = 400
                elif rec.total_gross_sales <= 50000:
                    cap = 500
                elif rec.total_gross_sales <= 100000:
                    cap = 1000
                else:
                    cap = 2000

                rec.entertainment_claim = min(total, cap)

    @api.onchange('entertainment_line_ids')
    def _warn_entertainment_excess(self):
        for rec in self:
            total = sum(line.amount for line in rec.entertainment_line_ids)
            if rec.entertainment_claim < total and rec.sales_type == 'outdoor':
                return {
                    'warning': {
                        'title': "Claim Exceeds Limit",
                        'message': "Total entertainment claim exceeds the maximum allowed based on gross sales.",
                    }
                }

    car_allowance = fields.Monetary(string="Car Allowance", compute="_compute_claims", store=True)

    toll_claim = fields.Monetary(
        string="Toll Claims",
        compute="_compute_toll_claim",
        currency_field='currency_id',
        store=True
    )

    toll_line_ids = fields.One2many(
        'expense.toll.line',
        'expense_id',
        string="Toll Lines"
    )

    @api.depends('toll_line_ids.amount')
    def _compute_toll_claim(self):
        for rec in self:
            rec.toll_claim = sum(line.amount for line in rec.toll_line_ids)

    petrol_local = fields.Monetary(
        string="Petrol (Local) Claims",
        compute="_compute_petrol_by_type",
        currency_field='currency_id',
        store=True
    )

    petrol_outstation = fields.Monetary(
        string="Petrol (Outstation) Claims",
        compute="_compute_petrol_by_type",
        currency_field='currency_id',
        store=True
    )

    petrol_line_ids = fields.One2many(
        'expense.petrol.line',
        'expense_id',
        string="Petrol Claims"
    )

    @api.depends('petrol_line_ids.amount', 'petrol_line_ids.petrol_type')
    def _compute_petrol_by_type(self):
        for rec in self:
            local = 0.0
            outstation = 0.0
            for line in rec.petrol_line_ids:
                if line.petrol_type == 'local':
                    local += line.amount
                elif line.petrol_type == 'outstation':
                    outstation += line.amount
            rec.petrol_local = min(local, 400)  # Local capped at RM400
            rec.petrol_outstation = outstation

    outstation_line_ids = fields.One2many(
        'expense.outstation.line',
        'expense_id',
        string="Accommodation Claims"
    )

    accommodation_total = fields.Monetary(
        string="Accommodation Claims",
        compute="_compute_accommodation_total",
        currency_field='currency_id',
        store=True
    )

    @api.depends('outstation_line_ids.amount')
    def _compute_accommodation_total(self):
        for rec in self:
            rec.accommodation_total = sum(line.amount for line in rec.outstation_line_ids)

    commission_claimed = fields.Monetary(string="Commission Claimed",compute="_compute_claims",store=True,readonly=True)
    new_customer_incentive_claimed = fields.Monetary(string="New Customer Incentive Claimed")

    car_allowance_max = fields.Monetary(
        string="Max Car Allowance",
        compute="_compute_car_allowance_max",
        currency_field='currency_id',
        store=True
    )

    @api.depends('total_gross_sales', 'sales_type')
    def _compute_car_allowance_max(self):
        for rec in self:
            if rec.sales_type != 'outdoor':
                rec.car_allowance_max = 0.0
            elif 50000 <= rec.total_gross_sales <= 69999:
                rec.car_allowance_max = 3000
            elif 70000 <= rec.total_gross_sales <= 99999:
                rec.car_allowance_max = 4000
            elif rec.total_gross_sales >= 100000:
                rec.car_allowance_max = 5000
            else:
                rec.car_allowance_max = 0.0

    car_allowance_claimed = fields.Monetary(
        string="Car Allowance Claims",
        compute="_compute_car_allowance_claimed",
        currency_field='currency_id',
        store=True
    )

    car_allowance_line_ids = fields.One2many(
        'expense.car.allowance.line',
        'expense_id',
        string="Car Allowance Claims"
    )

    @api.depends('car_allowance_line_ids.amount')
    def _compute_car_allowance_claimed(self):
        for rec in self:
            total = sum(line.amount for line in rec.car_allowance_line_ids)
            rec.car_allowance_claimed = min(total, rec.car_allowance or 0.0)

    total_claimable = fields.Monetary(
        string="Total Claimable",
        compute="_compute_total_claimable",
        currency_field='currency_id',
        store=True
    )

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)

    @api.depends('commission_line_ids', 'sales_type', 'gross_profit', 'customer_type', 'new_customer_ids', 'total_gross_sales')
    def _compute_claims(self):
        for rec in self:
            # === Commission Calculation ===
            commission_rate = 0.12 if rec.sales_type == 'outdoor' else 0.03 if rec.sales_type == 'indoor' else 0.0
            commission_base = sum(line.invoice_amount for line in rec.commission_line_ids)
            rec.commission = commission_base * commission_rate
            rec.commission_claimed = rec.commission

            # === New Customer Incentive ===
            if self.total_gross_sales > 1000:
                rec.new_customer_incentive = len(rec.new_customer_ids) * 200.0
            else:
                rec.new_customer_incentive = 0

            # === Car Allowance ===
            rec.car_allowance = 0.0
            if rec.sales_type == 'outdoor':
                if 50000 <= self.total_gross_sales <= 69999:
                    rec.car_allowance = 3000
                elif 70000 <= self.total_gross_sales <= 99999:
                    rec.car_allowance = 4000
                elif self.total_gross_sales >= 100000:
                    rec.car_allowance = 5000

    total_gross_sales = fields.Monetary(string="Total Gross Sales", compute="_compute_total_gross_sales", store=True)

    @api.depends('commission_line_ids.invoice_amount')
    def _compute_total_gross_sales(self):
        for rec in self:
            rec.total_gross_sales = sum(line.invoice_amount for line in rec.commission_line_ids)

    @api.onchange(
        'commission_claimed', 'new_customer_incentive_claimed',
        'entertainment_claimed', 'car_allowance_claimed', 'petrol_local'
    )
    def _check_claim_limits(self):
        for rec in self:
            if rec.commission_claimed and rec.commission:
                rec.commission_claimed = min(rec.commission_claimed, rec.commission)
            if rec.new_customer_incentive_claimed and rec.new_customer_incentive:
                rec.new_customer_incentive_claimed = min(rec.new_customer_incentive_claimed, rec.new_customer_incentive)
            if rec.entertainment_claimed and rec.entertainment_claim:
                rec.entertainment_claimed = min(rec.entertainment_claimed, rec.entertainment_claim)
            if rec.car_allowance_claimed and rec.car_allowance:
                rec.car_allowance_claimed = min(rec.car_allowance_claimed, rec.car_allowance)
            if rec.petrol_local and rec.petrol_local > 400:
                rec.petrol_local = 400.0

    @api.depends(
        'commission_claimed', 'new_customer_incentive_claimed',
        'entertainment_claimed', 'car_allowance_claimed',
        'toll_claim', 'petrol_local', 'petrol_outstation', 'new_customer_ids', 'accommodation_total'
    )
    def _compute_total_claimable(self):
        for rec in self:
            new_customer_incentive = len(rec.new_customer_ids) * 200.0
            total = sum([
                rec.commission_claimed or 0.0,
                new_customer_incentive,
                rec.entertainment_claimed or 0.0,
                rec.car_allowance_claimed or 0.0,
                rec.toll_claim or 0.0,
                rec.petrol_local or 0.0,
                rec.petrol_outstation or 0.0,
                rec.accommodation_total or 0.0,
            ])
            rec.total_claimable = total
            rec.total_amount_currency = total

class ExpenseNewCustomerLine(models.Model):
    _name = 'expense.new.customer.line'
    _description = 'New Customer Claimed'

    expense_id = fields.Many2one('hr.expense', string="Expense Reference", required=True, ondelete='cascade')
    customer_id = fields.Many2one('res.partner', string="Customer", domain="[('is_company','=',True)]", required=True)

class ExpenseCommissionLine(models.Model):
    _name = 'expense.commission.line'
    _description = 'Commission Customer Line'

    expense_id = fields.Many2one('hr.expense', string="Expense Reference", ondelete='cascade', required=True)
    customer_id = fields.Many2one('res.partner', string="Customer", required=True, domain="[('is_company','=',True)]")
    invoice_total = fields.Float(string="Invoice Amount", required=True)
    invoice_amount = fields.Float(string="Gross Profit", required=True)

class ExpenseTollLine(models.Model):
    _name = 'expense.toll.line'
    _description = 'Toll Claim Line'

    date = fields.Date(string="Date", default=fields.Date.today)
    expense_id = fields.Many2one('hr.expense', string="Expense", ondelete='cascade', required=True)
    destination = fields.Char(string="Destination")
    client_id = fields.Many2one('res.partner', string="Client", domain="[('is_company', '=', True)]")
    mileage = fields.Float(string="Mileage (km)")
    toll_location = fields.Char(string="Toll Location")
    amount = fields.Monetary(string="Amount (RM)")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)

class ExpenseOutstationTollLine(models.Model):
    _name = 'expense.outstation.toll.line'
    _description = 'Outstation Toll Claim Line'

    expense_id = fields.Many2one('hr.expense', string="Expense", ondelete='cascade')
    date = fields.Date(string="Date", default=fields.Date.today)
    destination = fields.Char(string="Destination")
    client_id = fields.Many2one('res.partner', string="Client", domain="[('is_company','=',True)]")
    mileage = fields.Float(string="Mileage (km)")
    toll_location = fields.Char(string="Toll Location")
    amount = fields.Monetary(string="Amount (RM)")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)


class ExpenseEntertainmentLine(models.Model):
    _name = 'expense.entertainment.line'
    _description = 'Entertainment Claim Line'

    expense_id = fields.Many2one('hr.expense', string="Expense", ondelete='cascade', required=True)
    date = fields.Date(string="Date", default=fields.Date.today)
    venue = fields.Char(string="Venue")
    location = fields.Char(string="Location")
    receipt_number = fields.Char(string="Receipt Number")
    client_id = fields.Many2one('res.partner', string="Client", domain="[('is_company', '=', True)]")
    amount = fields.Monetary(string="Amount (RM)")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)

class ExpenseOutstationLine(models.Model):
    _name = 'expense.outstation.line'
    _description = 'Outstation Claim Line'

    expense_id = fields.Many2one('hr.expense', string="Expense", ondelete='cascade', required=True)
    date = fields.Date(string="Date", default=fields.Date.today)
    hotel = fields.Char(string="Hotel")
    location = fields.Char(string="Location")
    num_days = fields.Integer(string="No. of Days")
    purpose = fields.Text(string="Purpose")
    amount = fields.Monetary(string="Amount (RM)")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)

class ExpensePetrolLine(models.Model):
    _name = 'expense.petrol.line'
    _description = 'Petrol Claim Line'

    expense_id = fields.Many2one('hr.expense', string="Expense", ondelete='cascade', required=True)
    date = fields.Date(string="Date", default=fields.Date.today)
    location = fields.Char(string="Location")
    petrol_station = fields.Char(string="Petrol Station")
    petrol_type = fields.Selection([
        ('local', 'Local'),
        ('outstation', 'Outstation')
    ], string="Local/Outstation")
    amount = fields.Monetary(string="Amount (RM)")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)

class ExpenseCarAllowanceLine(models.Model):
    _name = 'expense.car.allowance.line'
    _description = 'Car Allowance Line'

    expense_id = fields.Many2one('hr.expense', string="Expense", ondelete='cascade', required=True)
    date = fields.Date(string="Date", default=fields.Date.today)
    workshop = fields.Char(string="Workshop")
    location = fields.Char(string="Location")
    receipt_no = fields.Char(string="Receipt No")
    details = fields.Text(string="Details")
    amount = fields.Monetary(string="Amount (RM)")
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id.id)
