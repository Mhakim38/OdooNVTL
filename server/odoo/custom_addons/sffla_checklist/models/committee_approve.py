from odoo import models, fields, api
from odoo.exceptions import UserError

class SubscriptionPackage(models.Model):
    _inherit = 'subscription.package'

    committee_decision = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], string='Committee Decision', default='pending', tracking=True)

    stage_committee_next_id = fields.Many2one(
        'subscription.package.stage', string='Next Stage After Committee'
    )

    def action_approve_committee(self):
        for rec in self:
            if rec.stage_id.category != 'committee':
                raise UserError("Approve is only allowed in Committee stage.")
            # Move to draft stage (Approved)
            draft_stage = self.env['subscription.package.stage'].search(
                [('category', '=', 'draft')], limit=1
            )
            if not draft_stage:
                raise UserError("No stage with category 'draft' found.")
            rec.committee_decision = 'approved'
            rec.stage_id = draft_stage

    def action_reject_committee(self):
        for rec in self:
            if rec.stage_id.category != 'committee':
                raise UserError("Reject is only allowed in Committee stage.")

            rejected_stage = self.env['subscription.package.stage'].search(
                [('category', '=', 'reject')], limit=1
            )
            if not rejected_stage:
                raise UserError("No stage with category 'closed' found for rejected.")

            rec.committee_decision = 'rejected'
            rec.stage_id = rejected_stage
