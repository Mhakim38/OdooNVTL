# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)



class CompanyCircular(models.Model):
    _name = "company.circular"
    _description = "Company Circular"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "date desc, id desc"

    # -------------------------
    # Core fields
    # -------------------------
    name = fields.Char("Subject", required=True, tracking=True)
    number = fields.Char("Circular No.", tracking=True, index=True)
    date = fields.Date("Circular Date", default=fields.Date.context_today, tracking=True, required=True)
    department_id = fields.Many2one("hr.department", string="Issuing Department", tracking=True)
    author_id = fields.Many2one(
        "res.users", string="Author",
        default=lambda self: self.env.user,
        tracking=True, required=True
    )
    body = fields.Html(string="Circular Content")

    mysql_sequence = fields.Char(string="MySQL Sequence")
    file_ids = fields.One2many(
        "circular.file",
        "circular_id",
        string="Circular Files"
    )

    attachment_ids = fields.Many2many("ir.attachment", string="Attachments")
    category = fields.Selection([
        ('customs', 'Customs Affair'),
        ('education', 'Education & Training'),
        ('membership', 'Membership Affairs'),
        ('na', 'NA'),
        ('ncd', 'NCD & Maritime Affairs'),
        ('port', 'Port Operation'),
        ('social', 'Social & Recreation'),
        ('other', 'Other'),
        ('other_agent', 'Other Governing Agencies'),
        ('trade', 'Trade Facilitation'),
    ], string="Category")


    # -------------------------
    # Distribution
    # -------------------------
    recipient_mode = fields.Selection(
        [
            ("manual", "Choose Recipients"),
            ("all_contacts", "All Contacts"),
            ("all_employees", "All Employees"),
            ("all_users", "All Users"),
        ],
        string="Recipient Mode",
        default="manual",
        required=True,
    )

    partner_ids = fields.Many2many("res.partner", string="Recipients (Contacts)")
    employee_ids = fields.Many2many("hr.employee", string="Recipients (Employees)")
    user_ids = fields.Many2many("res.users", string="Recipients (Users)")
    recipient_count = fields.Integer(compute="_compute_recipient_count", store=False)

    # -------------------------
    # Acknowledgement
    # -------------------------
    ack_ids = fields.One2many("company.circular.ack", "circular_id", string="Acknowledgements")
    ack_required = fields.Boolean("Require Acknowledgement", default=True)
    ack_deadline = fields.Date("Ack Deadline")
    ack_pending = fields.Integer(compute="_compute_ack_stats", string="Pending Acks", store=False)
    ack_done = fields.Integer(compute="_compute_ack_stats", string="Acknowledged", store=False)

    # -------------------------
    # Lifecycle
    # -------------------------
    state = fields.Selection([
        ("draft", "Draft"),
        ("published", "Published"),
        ("archived", "Archived"),
    ], default="draft", tracking=True)

    tag_ids = fields.Many2many("ir.tag", string="Tags")

    _sql_constraints = [
        ("unique_number", "unique(number)", "Circular number must be unique."),
    ]

    # -------------------------
    # Compute methods
    # -------------------------
    @api.depends("recipient_mode", "partner_ids", "employee_ids", "user_ids")
    def _compute_recipient_count(self):
        for rec in self:
            partners = set()
            if rec.recipient_mode == "manual":
                partners |= set(rec.partner_ids.ids)

                # handle employee partner links
                if "work_contact_id" in rec.employee_ids._fields:
                    partners |= set(rec.employee_ids.mapped("work_contact_id").ids)
                elif "private_address_id" in rec.employee_ids._fields:
                    partners |= set(rec.employee_ids.mapped("private_address_id").ids)
                elif "address_home_id" in rec.employee_ids._fields:
                    partners |= set(rec.employee_ids.mapped("address_home_id").ids)

                partners |= set(rec.user_ids.mapped("partner_id").ids)

            elif rec.recipient_mode == "all_contacts":
                partners |= set(self.env["res.partner"].search([]).ids)

            elif rec.recipient_mode == "all_employees":
                if "work_contact_id" in self.env["hr.employee"]._fields:
                    partners |= set(self.env["hr.employee"].search([]).mapped("work_contact_id").ids)
                elif "address_home_id" in self.env["hr.employee"]._fields:
                    partners |= set(self.env["hr.employee"].search([]).mapped("address_home_id").ids)

            elif rec.recipient_mode == "all_users":
                partners |= set(self.env["res.users"].search([]).mapped("partner_id").ids)

            rec.recipient_count = len([p for p in partners if p])

    @api.depends("ack_ids.state")
    def _compute_ack_stats(self):
        for rec in self:
            rec.ack_done = sum(1 for a in rec.ack_ids if a.state == "done")
            rec.ack_pending = sum(1 for a in rec.ack_ids if a.state == "pending")

    # -------------------------
    # Helpers
    # -------------------------
    def _gather_all_partners(self):
        """Return a deduplicated recordset of res.partner from recipients based on mode."""
        self.ensure_one()
        partners = self.env["res.partner"]

        if self.recipient_mode == "manual":
            partners = (
                    self.partner_ids
                    | self.user_ids.mapped("partner_id")
            )
            if "work_contact_id" in self.employee_ids._fields:
                partners |= self.employee_ids.mapped("work_contact_id")
            elif "private_address_id" in self.employee_ids._fields:
                partners |= self.employee_ids.mapped("private_address_id")
            elif "address_home_id" in self.employee_ids._fields:
                partners |= self.employee_ids.mapped("address_home_id")

        elif self.recipient_mode == "all_contacts":
            partners = self.env["res.partner"].search([])

        elif self.recipient_mode == "all_employees":
            employees = self.env["hr.employee"].search([])
            if "work_contact_id" in employees._fields:
                partners = employees.mapped("work_contact_id")
            elif "private_address_id" in employees._fields:
                partners = employees.mapped("private_address_id")
            elif "address_home_id" in employees._fields:
                partners = employees.mapped("address_home_id")

        elif self.recipient_mode == "all_users":
            partners = self.env["res.users"].search([]).mapped("partner_id")

        return partners.filtered(lambda p: p)

    def _get_recipient_emails(self):
        """Return a comma-separated string of recipient emails."""
        self.ensure_one()
        partners = self._gather_all_partners()
        emails = [p.email.strip() for p in partners if p.email]
        emails = list(set(emails))  # deduplicate
        _logger.info("📧 Final recipient emails for circular %s: %s", self.name, emails)
        return ",".join(emails) if emails else False

    # -------------------------
    # Actions
    # -------------------------
    sender_name = fields.Char(string="Sender Name")
    sender_email = fields.Char(string="Sender Email")

    def action_publish(self):
        for rec in self:
            if rec.state != "draft":
                raise UserError(_("Only drafts can be published."))

            partners = rec._gather_all_partners()
            if not partners:
                raise UserError(_("Please add at least one recipient before publishing."))

            rec.message_subscribe(partners.ids)

            template = self.env.ref(
                "sffla_circular_new.circular_email_template",
                raise_if_not_found=False
            )
            if not template:
                raise UserError(_("Email template not found."))

            for partner in partners:
                if not partner.email:
                    continue

                # Create mail in outbox (DO NOT force_send here)
                template.send_mail(
                    rec.id,
                    force_send=False,  # stays in queue
                    email_values={'email_to': partner.email,
                                  'partner_ids': [partner.id],
                                  'attachment_ids': [(6, 0, rec.attachment_ids.ids)],}
                )

            _logger.info("📨 Queued %s mails for circular %s", len(partners), rec.id)

            rec.state = "published"

    def action_archive(self):
        for rec in self:
            rec.state = "archived"

    def action_reset_to_draft(self):
        for rec in self:
            if rec.state == "published":
                raise UserError(_("Cannot reset a published circular to draft. Archive instead."))
            rec.state = "draft"


class CompanyCircularAck(models.Model):
    _name = "company.circular.ack"
    _description = "Circular Acknowledgement"
    _order = "state, id desc"

    category = fields.Selection([
        ('customs', 'Customs Affair'),
        ('education', 'Education & Training'),
        ('membership', 'Membership Affairs'),
        ('na', 'NA'),
        ('ncd', 'NCD & Maritime Affairs'),
        ('port', 'Port Operation'),
        ('social', 'Social & Recreation'),
        ('trade', 'Trade Facilitation'),
    ], string="Category")
    circular_id = fields.Many2one("company.circular", required=True, ondelete="cascade")
    partner_id = fields.Many2one("res.partner", string="Recipient (Partner)", required=True, index=True)
    user_id = fields.Many2one("res.users", string="Recipient (User)")
    state = fields.Selection([("pending", "Pending"), ("done", "Acknowledged")], default="pending", index=True)
    date_ack = fields.Datetime("Acknowledged On", readonly=True)
    deadline = fields.Date("Deadline")
    note = fields.Char("Note")

    _sql_constraints = [
        ("uniq_ack_per_partner", "unique(circular_id, partner_id)",
         "This recipient already has an acknowledgement for this circular."),
    ]

    def action_acknowledge(self):
        for rec in self:
            if rec.state == "done":
                continue
            rec.write({
                "state": "done",
                "date_ack": fields.Datetime.now(),
            })
            rec.circular_id.message_post(
                body=_("Acknowledged by %s.") % (rec.partner_id.display_name,),
                partner_ids=[rec.partner_id.id],
                subtype_xmlid="mail.mt_comment",
            )

class CircularTagCategory(models.Model):
    _name = "circular.tag.category"
    _description = "Circular Tag Category"
    _order = "name"

    name = fields.Char("Name", required=True, index=True)
    color = fields.Integer("Color Index")
    description = fields.Text("Description")

class CompanyCircular(models.Model):
    _inherit = "company.circular"

    tag_ids = fields.Many2many(
        comodel_name="circular.tag.category",
        relation="circular_tag_rel",  # M2M table name
        column1="circular_id",  # FK to company.circular
        column2="category_id",  # FK to circular.tag.category
        string="Tags",
    )

    def action_send_mail(self):
        template = self.env.ref("sffla_circular_new.circular_email_template", raise_if_not_found=False)
        if not template:
            raise UserError("Email template not found. Please configure it.")

        for rec in self:
            partners = rec._gather_all_partners()
            if not partners:
                raise UserError("No recipients found.")

            # Send using the template
            template.send_mail(rec.id, force_send=True)

class CircularFile(models.Model):
    _name = "circular.file"
    _description = "Circular File"

    # Link to Circular
    circular_id = fields.Many2one(
        "company.circular",
        string="Circular",
        required=True,
        ondelete="cascade"
    )

    # Related name from company.circular
    name = fields.Char(
        string="Circular Title",
        related="circular_id.name",
        store=True,
        readonly=True
    )

    # Related mysql_sequence from company.circular
    mysql_sequence = fields.Char(
        string="Circular Sequence",
        related="circular_id.mysql_sequence",
        store=True,
        readonly=True
    )

    # Attachments linked to this circular
    attachment_ids = fields.Many2many(
        "ir.attachment",
        string="Files"
    )



