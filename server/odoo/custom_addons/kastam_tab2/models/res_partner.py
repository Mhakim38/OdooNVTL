from odoo import models, fields

#This is a Contacts (res.partner)
class ResPartner(models.Model):
    _inherit = "res.partner"

    # Kastam fields
    kastam_registration_number = fields.Char("Kastam Registration Number")

    expiry_date = fields.Date(
        string="Expiry Date"
    )

    # Services fields
    shipping_agent = fields.Boolean(string="Shipping Agent")
    forwarding_agents = fields.Boolean(string="Forwarding Agents / Customs Brokerage")
    last_mile_delivery = fields.Boolean(string="Last Mile Delivery")
    transport_operators = fields.Boolean(string="Transport Operators")
    freight_forwarding = fields.Boolean(string="Freight Forwarding")
    courier_services = fields.Boolean(string="Courier Services")
    warehouse_operators = fields.Boolean(string="Warehouse Operators")
    combined_transport_operators = fields.Boolean(string="Combined Transport Operators")
    nvocc = fields.Boolean(string="NVOCC")
    ancillary_services = fields.Boolean(string="Ancillary Services")

    # KASTAM Detail file
    approval_letter = fields.Binary(string="Approval Letter (BF/BS/BZ or others)")
    approval_letter_filename = fields.Char(string="Approval Letter Filename")

    audited_account = fields.Binary(string="Last Audited Account")
    audited_account_filename = fields.Char(string="Last Audited Account Filename")

    roc_rob = fields.Binary(string="ROC / ROB")
    roc_rob_filename = fields.Char(string="ROC/ROB Filename")


    # SSM Detail file
    form_9 = fields.Binary(string="Form 9")
    form_9_filename = fields.Char(string="Form 9 Filename")

    form_13 = fields.Binary(string="Form 13")
    form_13_filename = fields.Char(string="Form 13 Filename")

    form_49 = fields.Binary(string="Form 49")
    form_49_filename = fields.Char(string="Form 49 Filename")

    form_24 = fields.Binary(string="Form 24")
    form_24_filename = fields.Char(string="Form 24 Filename")

    # Company details
    incorporation_date = fields.Date(string="Incorporation Date")
    company_reg_no = fields.Char(string="Company Reg No")
    business_entity = fields.Selection([
        ('entity1', 'Private Limited'),
        ('entity2', 'Limited'),
        ('entity3', 'Sole Proprietorship'),
        ('entity4', 'Partnership'),
        ('entity5', 'Subsidiary'),
        ('entity6', 'Association'),
        ('entity7', 'Academic Institution'),
        ('entity8', 'Software Applications Vendor'),
        ('entity9', 'Suppliers'),
    ], string="Business Entity")

    authorized_capital = fields.Monetary(string="Authorized Capital")
    paid_up_capital = fields.Monetary(string="Paid-up Capital")
    currency_id = fields.Many2one("res.currency", string="Currency")  # required for Monetary

    malaysia_bank = fields.Selection([
        ('maybank', 'Maybank (Malayan Banking Berhad)'),
        ('cimb', 'CIMB Bank'),
        ('public_bank', 'Public Bank Berhad'),
        ('rhb', 'RHB Bank'),
        ('ambank', 'AmBank'),
        ('bank_islam', 'Bank Islam Malaysia'),
        ('bank_rakyat', 'Bank Rakyat'),
        ('hsbc', 'HSBC Bank Malaysia'),
        ('ocbc', 'OCBC Bank Malaysia'),
        ('uob', 'UOB Malaysia'),
        ('bank_muamalat', 'Bank Muamalat'),
        ('standard_chartered', 'Standard Chartered Malaysia'),
        ('affin_bank', 'Affin Bank'),
        ('alliance_bank', 'Alliance Bank'),
        ('agrobank', 'Agrobank'),
        ('kuwait_finance', 'Kuwait Finance House'),
        ('citibank', 'Citibank Malaysia'),
        ('al_rajhi', 'Al Rajhi Bank'),
        ('bnp_paribas', 'BNP Paribas Malaysia'),
        ('scotiabank', 'Scotiabank Malaysia'),
    ], string="Bank in Malaysia")

    # # Authorized representative details
    # company_association_institution = fields.Char(
    #     string="Name of Company / Association / Institution"
    # )
    registration_address = fields.Char(string="Registration Address")
    auth_rep_1 = fields.Char(string="Authorized Representative 1")
    auth_rep_2 = fields.Char(string="Authorized Representative 2")

    subscription_id = fields.Many2one(
        'subscription.package',
        string="Subscription Package"
    )

    subscription_date_start = fields.Date(
        string="Subscription Start Date",
        related="subscription_id.date_started",  # adjust to your actual relation field
        store=True,
        readonly=True
    )

    subscription_next_invoice_date = fields.Date(
        string="Next Invoice Date",
        related="subscription_id.next_invoice_date",  # adjust relation
        store=True,
        readonly=True
    )

    member_id_new = fields.Char(
        string="I.D (NEW)",
        related="membership_id.membership_number",  # membership_id comes from sffla_ordinary
        store=True,
        readonly=True
    )


