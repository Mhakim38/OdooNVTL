from odoo import models, fields

class ResPartner(models.Model):
    _inherit = "res.partner"

    kastam_registration_number = fields.Char("Kastam Registration Number")
    expiry_date = fields.Date("Kastam Expiry Date")
    approval_letter = fields.Binary("Approval Letter")
    audited_account = fields.Binary("Audited Account")
    roc_rob = fields.Binary("ROC/ROB")

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

    incorporation_date = fields.Date("Incorporation Date")
    company_reg_no = fields.Char("Company Reg No")
    business_entity = fields.Char("Business Entity")
    authorized_capital = fields.Float("Authorized Capital")
    paid_up_capital = fields.Float("Paid Up Capital")
    malaysia_bank = fields.Char("Malaysia Bank")
    registration_address = fields.Char("Registration Address")
    auth_rep_1 = fields.Char("Authorized Representative 1")
    auth_rep_2 = fields.Char("Authorized Representative 2")

    # SSM Detail file
    form_9 = fields.Binary(string="Form 9")
    form_9_filename = fields.Char(string="Form 9 Filename")

    form_13 = fields.Binary(string="Form 13")
    form_13_filename = fields.Char(string="Form 13 Filename")

    form_49 = fields.Binary(string="Form 49")
    form_49_filename = fields.Char(string="Form 49 Filename")

    form_24 = fields.Binary(string="Form 24")
    form_24_filename = fields.Char(string="Form 24 Filename")