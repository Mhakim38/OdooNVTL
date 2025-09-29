from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SubscriptionPackageVerifyChecklist(models.Model):
    _name = "subscription.package.verify.checklist"
    _description = "Subscription Package Verify Checklist"

    subscription_id = fields.Many2one(
        comodel_name="subscription.package",
        string="Subscription",
        required=True,
        ondelete="cascade"
    )
    name = fields.Char(
        string="Checklist Item",
        required=True
    )
    employee_id = fields.Many2one(
        comodel_name="res.users",
        string="Assigned Employee"
    )
    is_done = fields.Boolean(
        string="Done",
        default=False
    )


class SubscriptionPackage(models.Model):
    _inherit = "subscription.package"

    verify_checklist_ids = fields.One2many(
        comodel_name="subscription.package.verify.checklist",
        inverse_name="subscription_id",
        string="Verify Checklist",
        help="Checklist items for verification stage"
    )

    all_verify_done = fields.Boolean(
        string="All Verify Done",
        compute="_compute_all_verify_done",
        store=True
    )

    # -----------------------------
    # Helpers
    # -----------------------------
    def _add_default_verify_checklist(self):
        """Add default checklist items if stage is 'verify' and no checklist exists."""
        self.ensure_one()
        if self.stage_category == "verify" and not self.verify_checklist_ids:
            default_items = [
                {"name": "Customer Details Verified"},
                {"name": "Documents Collected"},
                {"name": "Eligibility Checked"},
            ]
            self.verify_checklist_ids = [(0, 0, item) for item in default_items]

    # -----------------------------
    # Compute Methods
    # -----------------------------
    @api.depends("verify_checklist_ids.is_done")
    def _compute_all_verify_done(self):
        for rec in self:
            rec.all_verify_done = bool(rec.verify_checklist_ids) and all(
                item.is_done for item in rec.verify_checklist_ids
            )

    # -----------------------------
    # Create / Write Overrides
    # -----------------------------
    @api.model
    def create(self, vals):
        record = super().create(vals)
        record._add_default_verify_checklist()
        return record

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec._add_default_verify_checklist()
        return res

    # -----------------------------
    # Onchange
    # -----------------------------
    @api.onchange("stage_id")
    def _onchange_stage_id(self):
        """Auto add default checklist when entering Verify stage (form UI only)."""
        self._add_default_verify_checklist()

    # -----------------------------
    # Actions
    # -----------------------------
    def action_verified(self):
        """Move to the next stage once verified."""
        for rec in self:
            if rec.stage_category != "verify":
                continue

            if not rec.all_verify_done:
                raise UserError(_("Please complete all checklist items before verifying."))

            next_stage = self.env["subscription.package.stage"].search(
                [("sequence", ">", rec.stage_id.sequence)],
                order="sequence asc",
                limit=1,
            )
            if not next_stage:
                raise UserError(_("No next stage found. Please configure stages correctly."))

            rec.write({"stage_id": next_stage.id})
            rec.message_post(
                body=_("Stage changed to <b>%s</b> after verification.") % next_stage.name
            )
