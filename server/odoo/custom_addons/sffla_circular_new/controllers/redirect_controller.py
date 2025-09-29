from odoo import http
from odoo.http import request
import urllib.parse

class RedirectController(http.Controller):

    @http.route('/r/<string:code>', type='http', auth='public', website=True, csrf=False)
    def redirect_to_form(self, code, **kwargs):
        """
        Redirect Odoo tracked links to external forms.
        """
        # Lookup mapping
        redirect_map = {
            "QdmMvZJhfF": "https://forms.office.com/r/QdmMvZJhfF",
        }

        target_url = redirect_map.get(code)
        if not target_url:
            return "Link not found", 404

        # Preserve query parameters safely
        query_string = request.httprequest.query_string.decode()
        if query_string:
            # Properly append using urllib to avoid broken URLs
            target_url = target_url + "?" + urllib.parse.quote_plus(query_string, safe="=&")

        return request.redirect(target_url, code=302)
