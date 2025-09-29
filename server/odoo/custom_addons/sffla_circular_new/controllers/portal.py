from odoo import http
from odoo.http import request

class PortalMassMailing(http.Controller):

    @http.route(['/portal/mass_mailing_detail/<int:mailing_id>'], type='http', auth="user", website=True)
    def portal_mass_mailing_detail(self, mailing_id, **kwargs):
        mailing = request.env['mailing.mailing'].sudo().browse(mailing_id)
        return request.render("sffla_circular.portal_mass_mailing_detail", {
            'mailing': mailing
        })

    @http.route(['/portal/my_mass_mailings'], type='http', auth="user", website=True)
    def portal_my_mass_mailings(self, search='', msg_type='all', **kwargs):
        # Show only completed/sent mailings
        domain = [('state', '=', 'done')]

        if search:
            domain += ['|', ('subject', 'ilike', search), ('body_html', 'ilike', search)]

        if msg_type != 'all':
            domain.append(('mailing_type', '=', msg_type))

        mailings = request.env['mailing.mailing'].sudo().search(domain)

        return request.render("sffla_circular.portal_my_mass_mailings", {
            'mailings': mailings,
            'search': search,
            'current_status': 'done',  # match actual state value
            'current_type': msg_type,
        })

