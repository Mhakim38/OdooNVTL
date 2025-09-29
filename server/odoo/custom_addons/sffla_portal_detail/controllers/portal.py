from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class PortalCustom(http.Controller):

    @http.route(['/my/home'], type='http', auth='user', website=True)
    def portal_my_home_custom(self, **kw):
        return request.render("sffla_portal.portal_my_home_custom", {})

class Portal(http.Controller):

    # ========== Partner Detail ==========
    @http.route(['/my/partner'], type='http', auth='user', website=True)
    def portal_partner(self, **kw):
        partner = request.env.user.partner_id.sudo()
        return request.render("sffla_portal_detail.portal_my_partner", {
            'partner': partner,
        })

    # ========== Kastam Detail ==========
    @http.route(['/my/kastam'], type='http', auth='user', website=True)
    def portal_kastam(self, **kw):
        partner = request.env.user.partner_id.sudo()
        _logger.info("=== Portal Kastam Partner === %s (ID: %s)", partner.name, partner.id)
        values = {
            'partner': partner,
            'active_page': 'kastam',
        }
        # gunakan request.render() dan id baru
        return request.render("sffla_portal_detail.portal_my_kastam", values)

    # ========== Services ==========
    @http.route(['/my/services'], type='http', auth='user', website=True)
    def portal_services(self, **kw):
        partner = request.env.user.partner_id.sudo()

        # Define service fields
        services = [
            ("Shipping Agent", partner.shipping_agent),
            ("Forwarding Agents", partner.forwarding_agents),
            ("Last Mile Delivery", partner.last_mile_delivery),
            ("Transport Operators", partner.transport_operators),
            ("NVOCC", partner.nvocc),
            ("Freight Forwarding", partner.freight_forwarding),
            ("Courier Services", partner.courier_services),
            ("Warehouse Operators", partner.warehouse_operators),
            ("Combined Transport Operators", partner.combined_transport_operators),
            ("Ancillary Services", partner.ancillary_services),
        ]

        # Filter only active (True)
        active_services = [(label, val) for label, val in services if val]

        values = {
            'partner': partner,
            'active_page': 'services',
            'active_services': active_services,
        }
        return request.render("sffla_portal_detail.portal_my_services", values)

    # ========== SSM Detail ==========
    @http.route(['/my/ssm'], type='http', auth='user', website=True)
    def portal_ssm(self, **kw):
        partner = request.env.user.partner_id.sudo()
        _logger.info("=== Portal SSM Partner === %s (ID: %s)", partner.name, partner.id)
        values = {
            'partner': partner,
            'active_page': 'ssm',
        }
        return request.render("sffla_portal_detail.portal_my_ssm", values)

    # ========== Membership Detail ==========
    @http.route(['/my/membership'], type='http', auth='user', website=True)
    def portal_my_membership(self, **kw):
        partner = request.env.user.partner_id
        memberships = request.env['res.members'].sudo().search([
            ('id', '=', partner.membership_id.id)
        ])
        return request.render("sffla_portal_detail.portal_my_membership", {
            'partner': partner,
            'memberships': memberships,
        })


