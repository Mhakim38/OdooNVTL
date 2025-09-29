from odoo import models, fields, api

#This is a membership subscription (subscription.package)
class SubscriptionPackage(models.Model):
    _inherit = 'subscription.package'

    proposer_company = fields.Many2one("res.partner", string="Proposer Company")
    proposer_name = fields.Char(string="Proposer Name")
    proposer_id_new = fields.Char(
        string="Proposer ID (NEW)",
        compute="_compute_proposer_id_new",
        store=True,
        readonly=True
    )

    # Change the UI named susbscription plan to Membership Type - Hakim
    plan_id = fields.Many2one(
        'subscription.package.plan',
        string='Membership Type',
    )

    seconder_company = fields.Many2one("res.partner", string="Seconder Company")
    seconder_name = fields.Char(string="Seconder Name")
    seconder_id_new = fields.Char(
        string="Seconder ID (NEW)",
        compute="_compute_seconder_id_new",
        store=True,
        readonly=True
    )

    partner_member_id_new = fields.Char(
        string="Member I.D (NEW)",
        related="partner_id.member_id_new",
        store=True,
        readonly=True
    )

    @api.depends('proposer_company')
    def _compute_proposer_id_new(self):
        for rec in self:
            rec.proposer_id_new = rec.proposer_company.membership_id.membership_number if rec.proposer_company and rec.proposer_company.membership_id else False

    @api.depends('seconder_company')
    def _compute_seconder_id_new(self):
        for rec in self:
            rec.seconder_id_new = rec.seconder_company.membership_id.membership_number if rec.seconder_company and rec.seconder_company.membership_id else False

    @api.depends('partner_id')
    def _compute_member_id_new(self):
        for rec in self:
            rec.member_id_new = rec.partner_id.membership_id.membership_number if rec.partner_id and rec.partner_id.membership_id else False

    member_type = fields.Selection([
        ('ordinary', 'Ordinary Member'),
        ('corporate', 'Corporate Member'),
        ('honorary', 'Associate Member')
    ], string="Member Type")

    principal_id = fields.Many2one('res.partner', string="Principal Member")
    member_id_old = fields.Char(string="I.D (OLD)")

    proposer_id_old = fields.Char(string="Proposer ID (OLD)")
    seconder_id_old = fields.Char(string="Seconder ID (OLD)")

    applicant_name = fields.Char(string="Applicant Name")

    application_date = fields.Date(string="Application Date")

    ncd = fields.Boolean(string="NCD")  # or fields.Char if it's text

    member_date_start = fields.Date(string="Membership Start Date")
    member_date_end = fields.Date(string="Membership End Date")

    approval_letter = fields.Binary(related="partner_id.approval_letter", readonly=False)
    approval_letter_filename = fields.Char(related="partner_id.approval_letter_filename", readonly=False)

    audited_account = fields.Binary(related="partner_id.audited_account", readonly=False)
    audited_account_filename = fields.Char(related="partner_id.audited_account_filename", readonly=False)

    roc_rob = fields.Binary(related="partner_id.roc_rob", readonly=False)
    roc_rob_filename = fields.Char(related="partner_id.roc_rob_filename", readonly=False)

    form_9 = fields.Binary(related="partner_id.form_9", readonly=False)
    form_9_filename = fields.Char(related="partner_id.form_9_filename", readonly=False)

    form_13 = fields.Binary(related="partner_id.form_13", readonly=False)
    form_13_filename = fields.Char(related="partner_id.form_13_filename", readonly=False)

    form_49 = fields.Binary(related="partner_id.form_49", readonly=False)
    form_49_filename = fields.Char(related="partner_id.form_49_filename", readonly=False)

    form_24 = fields.Binary(related="partner_id.form_24", readonly=False)
    form_24_filename = fields.Char(related="partner_id.form_24_filename", readonly=False)
