from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    reg_full_address = fields.Text(string="Registration Address")
    biz_full_address = fields.Text(string="Business Address")
    circular_email = fields.Char(string="Circular Email")
