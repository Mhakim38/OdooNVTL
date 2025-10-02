from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = "sale.order"

    quotation_subject = fields.Char("Quotation Subject")
