# controllers/membership.py
import base64
from odoo import http
from odoo.http import request


class MembershipController(http.Controller):

    @http.route('/membership/apply2', type='http', auth='public', website=True)
    def membership_form(self, **kwargs):
        # Fetch all partners if still needed
        partners = request.env['res.partner'].sudo().search([('is_company', '=', True)])

        # Fetch all available subscription plans from the DB
        plans = request.env['subscription.package.plan'].sudo().search([])

        return request.render(
            "kastam_tab.membership_application_form2",
            {
                'partners': partners,
                'plans': plans,  # send records to the template
            }
        )

    @http.route('/membership/submit', type='http', auth='public', website=True, csrf=False)
    def membership_submit(self, **post):
        def _file_content_and_name(fieldname):
            """Return (base64_str_or_False, filename_or_False) for an <input type='file'/>."""
            f = request.httprequest.files.get(fieldname)
            if f and getattr(f, 'filename', ''):
                content = f.read()  # bytes
                return base64.b64encode(content), f.filename
            return False, False

        # 1) Prepare files (Binary + filename)
        approval_letter_b64, approval_letter_name = _file_content_and_name('approval_letter')
        audited_account_b64, audited_account_name = _file_content_and_name('audited_account')
        roc_rob_b64, roc_rob_name = _file_content_and_name('roc_rob')
        form9_b64, form9_name = _file_content_and_name('form_9')
        form13_b64, form13_name = _file_content_and_name('form_13')
        form49_b64, form49_name = _file_content_and_name('form_49')
        form24_b64, form24_name = _file_content_and_name('form_24')
        logo_b64, _logo_name = _file_content_and_name('company_logo')  # store to image_1920

        # 2) Get plan_id from the form (the template now posts plan_id directly)
        plan_id = int(post.get('plan_id') or 0)
        plan = request.env['subscription.package.plan'].sudo().browse(plan_id) if plan_id else False

        # 3) Create partner (map non-file fields too)
        partner_vals = {
            'is_company': True,
            'name': post.get('company_name') or 'New Applicant',
            'kastam_registration_number': post.get('kastam_registration_number'),
            'expiry_date': post.get('expiry_date'),
            'company_reg_no': post.get('company_reg_no'),
            'incorporation_date': post.get('incorporation_date'),
            'business_entity': post.get('business_entity'),
            'registration_address': post.get('registration_address'),

            'phone': post.get('telephone'),
            'street': post.get('business_address'),

            'auth_rep_1': post.get('auth_rep_1'),
            'auth_rep_2': post.get('auth_rep_2'),

            'authorized_capital': float(post.get('authorized_capital') or 0.0),
            'paid_up_capital': float(post.get('paid_up_capital') or 0.0),
            'currency_id': request.website.company_id.currency_id.id,

            'malaysia_bank': post.get('malaysia_bank'),

            # Services (checkboxes)
            'shipping_agent': 'shipping_agent' in post,
            'forwarding_agents': 'forwarding_agents' in post,
            'last_mile_delivery': 'last_mile_delivery' in post,
            'transport_operators': 'transport_operators' in post,
            'freight_forwarding': 'freight_forwarding' in post,
            'courier_services': 'courier_services' in post,
            'warehouse_operators': 'warehouse_operators' in post,
            'combined_transport_operators': 'combined_transport_operators' in post,
            'nvocc': 'nvocc' in post,
            'ancillary_services': 'ancillary_services' in post,

            # Binary files + filenames
            'approval_letter': approval_letter_b64,
            'approval_letter_filename': approval_letter_name,

            'audited_account': audited_account_b64,
            'audited_account_filename': audited_account_name,

            'roc_rob': roc_rob_b64,
            'roc_rob_filename': roc_rob_name,

            'form_9': form9_b64,
            'form_9_filename': form9_name,

            'form_13': form13_b64,
            'form_13_filename': form13_name,

            'form_49': form49_b64,
            'form_49_filename': form49_name,

            'form_24': form24_b64,
            'form_24_filename': form24_name,

            'image_1920': logo_b64,
        }

        partner = request.env['res.partner'].sudo().create(partner_vals)

        # 4) Create subscription.package linked to that partner
        subscription_vals = {
            'partner_id': partner.id,
            'applicant_name': post.get('your_name'),
            'application_date': post.get('application_date'),
            # removed obsolete member_type field
            'plan_id': plan_id,
            'proposer_company': int(post.get('proposer_company') or 0) or False,
            'seconder_company': int(post.get('seconder_company') or 0) or False,
            'proposer_name': post.get('proposer_name'),
            'seconder_name': post.get('seconder_name'),
        }
        request.env['subscription.package'].sudo().create(subscription_vals)

        return request.redirect('/thank-you')
