# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class PortalCircularController(http.Controller):

    @http.route(['/my/circulars'], type='http', auth="user", website=True)
    def portal_circulars(self, **kwargs):
        """List all circulars visible to the logged-in portal user"""
        user = request.env.user
        partner = user.partner_id

        # Fetch circulars where partner is a recipient
        circulars = request.env['company.circular'].sudo().search([
            '|',
            ('partner_ids', 'in', partner.id),
            ('user_ids', 'in', user.id),
            ('state', '=', 'published')
        ], order='date desc')

        return request.render('sffla_circular_new.portal_circulars_template', {
            'circulars': circulars
        })

    @http.route(['/my/circulars/<int:circular_id>'], type='http', auth="user", website=True)
    def portal_circular_detail(self, circular_id, **kwargs):
        """View details of a specific circular"""
        circular = request.env['company.circular'].sudo().browse(circular_id)
        if not circular.exists():
            return request.not_found()

        return request.render('sffla_circular_new.portal_circular_detail_template', {
            'circular': circular
        })


