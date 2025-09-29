{
    'name': 'SFFLA Portal Detail',
    'version': '1.0',
    'category': 'Website',
    'summary': 'Portal extension for Kastam & Company Details',
    'depends': ['base', 'portal', 'website', 'kastam_tab', 'sffla_ordinary', 'subscription_package', 'sffla_custom_address'],
    'data': [
        'security/ir.model.access.csv',
        'views/portal_nav.xml',
        'views/portal_detail.xml',
        'views/portal_home.xml',
            ],
    'installable': True,
    'application': False,
}
