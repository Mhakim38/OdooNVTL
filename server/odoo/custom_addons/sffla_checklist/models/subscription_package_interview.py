from odoo import models, fields, api, _

class SubscriptionPackageInterview(models.Model):
    _name = "subscription.package.interview"
    _description = "Subscription Package Interview"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    subscription_id = fields.Many2one(
        'subscription.package',
        string="Subscription",
        required=True,
        ondelete="cascade"
    )
    interviewer_id = fields.Many2one(
        'hr.employee',
        string="Interviewer",
        required=True
    )
    interview_date = fields.Datetime(
        string="Interview Date & Time",
        required=True
    )
    notes = fields.Text(string="Notes")

    status = fields.Selection(
        [
            ("scheduled", "Scheduled"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="scheduled",
        tracking=True,
        required=True,
    )

    event_id = fields.Many2one(
        "calendar.event",
        string="Calendar Event",
        ondelete="set null"
    )

    @api.model
    def create(self, vals):
        record = super().create(vals)

        # Create Calendar Event automatically
        if record.interviewer_id and record.interview_date:
            event = self.env["calendar.event"].create({
                "name": f"Interview: {record.subscription_id.name}",
                "start": record.interview_date,
                "stop": record.interview_date,  # can extend with duration
                "partner_ids": [(6, 0, [record.subscription_id.partner_id.id])],
                "description": record.notes or "",
            })
            record.event_id = event.id

        return record

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            if rec.event_id:
                rec.event_id.write({
                    "start": rec.interview_date,
                    "stop": rec.interview_date,
                    "description": rec.notes,
                })
        return res

    def action_open_calendar_event(self):
        self.ensure_one()
        if self.event_id:
            return {
                "name": "Calendar Event",
                "type": "ir.actions.act_window",
                "res_model": "calendar.event",
                "view_mode": "form",
                "res_id": self.event_id.id,
                "target": "current",
            }

class SubscriptionPackage(models.Model):
    _inherit = "subscription.package"

    interview_ids = fields.One2many(
        'subscription.package.interview',
        'subscription_id',
        string="Interviews"
    )

    interview_count = fields.Integer(
        string="Interviews",
        compute="_compute_interview_count"
    )

    def _compute_interview_count(self):
        for rec in self:
            rec.interview_count = self.env["subscription.package.interview"].search_count([
                ("subscription_id", "=", rec.id)
            ])


class SubscriptionPackage(models.Model):
    _inherit = "subscription.package"

    def action_interview_completed(self):
        """
        Mark interviews as completed and move subscription to the next stage.
        """
        for rec in self:
            # Make sure current stage is interview
            if rec.stage_id.category != 'interview':
                raise UserError(_("Interview Completed can only be done in Interview stage."))

            # Mark all interviews as completed
            rec.interview_ids.filtered(lambda i: i.status != 'completed').write({'status': 'completed'})

            # Move to the next stage (Committee)
            committee_stage = self.env['subscription.package.stage'].search(
                [('category', '=', 'committee')], limit=1
            )
            if not committee_stage:
                raise UserError(_("No stage with category 'committee' found."))

            rec.stage_id = committee_stage