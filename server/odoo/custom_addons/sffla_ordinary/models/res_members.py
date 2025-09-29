from odoo import models, fields, api
from datetime import datetime

class ResPartner(models.Model):
    _inherit = "res.partner"

    membership_id = fields.Many2one(
        "res.members",
        string="Membership",
        readonly=True
    )

    membership_number = fields.Char(
        string="Membership Number",
        related="membership_id.membership_number",
        store=True,
        readonly=True
    )


class ResMembers(models.Model):
    _name = "res.members"
    _description = "Members"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = "membership_number"

    partner_id = fields.Many2one(
        "res.partner",
        string="Member (Company)",
        required=True,
        tracking=True,
        ondelete="cascade",
        index=True,
        domain=[("is_company", "=", True)],  # only companies selectable
    )

    membership_number = fields.Char(
        string="Membership Number",
        required=True,
        copy=False,
        readonly=False,  # allow import / manual edit
        default="New",
        tracking=True
    )

    membership_status = fields.Selection(
        selection=[
            ('new', 'New'),
            ('active', 'Active'),
            ('expired', 'Expired'),
            ('cancelled', 'Cancelled'),
        ],
        string="Membership Status",
        required=True,
        default="new",
        tracking=True
    )

    membership_id = fields.Char(string="Member's I.D")

    membership_type = fields.Many2one(
        'subscription.package.plan',
        string="Membership Type"
    )

    join_month = fields.Selection(
        selection=[
            ('01', 'January'), ('02', 'February'), ('03', 'March'),
            ('04', 'April'), ('05', 'May'), ('06', 'June'),
            ('07', 'July'), ('08', 'August'), ('09', 'September'),
            ('10', 'October'), ('11', 'November'), ('12', 'December'),
        ],
        string="Join Month",
        tracking=True
    )

    join_year = fields.Selection(
        selection=[(str(y), str(y)) for y in range(1970, datetime.today().year + 5)],
        string="Join Year",
        required=True,
        tracking=True
    )

    _sql_constraints = [
        ('unique_membership_number',
         'unique(membership_number)',
         'Membership number must be unique!'),
        ('unique_partner',
         'unique(partner_id)',
         'Each partner can only have one membership!')
    ]

    @api.model
    def create(self, vals):
        # Block duplicate memberships for a partner
        existing = self.search([("partner_id", "=", vals.get("partner_id"))], limit=1)
        if existing:
            raise ValueError("This partner already has a membership!")

        # Case 1: If membership_number is provided (import / manual)
        if vals.get("membership_number") and vals["membership_number"] != "New":
            try:
                year_suffix = vals["membership_number"].split("/")[-1].strip()
                if len(year_suffix) == 2 and year_suffix.isdigit():
                    y2 = int(year_suffix)
                    if y2 >= 70:  # e.g. 73, 88 → 1973, 1988
                        vals["join_year"] = str(1900 + y2)
                    else:  # e.g. 00–69 → 2000–2069
                        vals["join_year"] = str(2000 + y2)
                elif len(year_suffix) == 4 and year_suffix.isdigit():
                    vals["join_year"] = year_suffix
            except Exception:
                pass

        # Case 2: Auto-generate membership_number if not provided
        else:
            company_code = "SFFLA"
            package_code = "OM"

            last_member = self.search([], order="id desc", limit=1)
            if last_member and last_member.membership_number:
                try:
                    last_seq = int(last_member.membership_number.split("/")[2])
                except Exception:
                    last_seq = 0
            else:
                last_seq = 0

            new_seq = str(last_seq + 1).zfill(3)

            year = vals.get("join_year", str(datetime.today().year))
            year_suffix = year[-2:]

            vals["membership_number"] = f"{company_code}/{package_code}/{new_seq}/{year_suffix}"

        # Create membership
        res = super(ResMembers, self).create(vals)

        # 🔑 Sync with partner
        if res.partner_id:
            res.partner_id.membership_id = res.id

        # 🔑 Activate automatically
        res.membership_status = "active"

        return res

    def action_set_active(self):
        for rec in self:
            rec.membership_status = "active"

    def action_set_expired(self):
        for rec in self:
            rec.membership_status = "expired"

    def action_set_cancelled(self):
        for rec in self:
            rec.membership_status = "cancelled"