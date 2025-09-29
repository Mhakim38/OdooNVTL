from odoo import models, fields, api

class ResMembers(models.Model):
    _name = "res.members"
    _description = "Members"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "membership_number"

    partner_id = fields.Many2one(
        "res.partner",
        string="Member (Company/Individual)",
        required=True,
        tracking=True
    )

    membership_number = fields.Char(
        string="Membership Number",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: "New",
        tracking=True
    )

    join_month = fields.Selection(
        selection=[
            ('01', 'January'),
            ('02', 'February'),
            ('03', 'March'),
            ('04', 'April'),
            ('05', 'May'),
            ('06', 'June'),
            ('07', 'July'),
            ('08', 'August'),
            ('09', 'September'),
            ('10', 'October'),
            ('11', 'November'),
            ('12', 'December'),
        ],
        string="Join Month",
        required=True,
        tracking=True
    )

    join_year = fields.Selection(
        selection=[(str(y), str(y)) for y in range(1970, 2025)],
        string="Join Year",
        required=True,
        tracking=True
    )

    @api.model
    def create(self, vals):
        if vals.get("membership_number", "New") == "New":
            vals["membership_number"] = self.env["ir.sequence"].next_by_code(
                "res.members.sequence"
            ) or "New"
        return super(ResMembers, self).create(vals)
