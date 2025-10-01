{
    'name': 'Subscription Package Kastam',
    'version': '17.0.1.0.0',   # adjust version to your Odoo version
    'summary': 'Adds Kastam Approved Registration details to Subscription Packages',
    'description': """
        This module extends Subscription Packages to include:
        - Kastam Approved Registration Number
        - Expiry Date
        Displayed in a dedicated notebook page called "Kastam Details".
    """,
    'author': 'Your Name/Company',
    'website': 'https://www.yourcompany.com',
    'category': 'Subscription',
    'license': 'LGPL-3',
    'depends': ['subscription_package','sffla_ordinary', 'base', 'contacts', 'mail'],  # dependency on subscription module
    'data': [
        'views/kastam_tab.xml',
        'views/resPartnerTab.xml',
        'views/web_form.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
