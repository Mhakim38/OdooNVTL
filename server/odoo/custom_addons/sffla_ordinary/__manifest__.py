{
    'name': 'SFFLA Ordinary Membership Management',
    'version': '17.0.1.0.0',
    'summary': 'Manage company memberships with numbers, statuses, and types',
    'description': """
Membership Management
======================
- Manage members linked to partners (companies only)
- Auto-generate or import membership numbers
- Track membership type, join month/year, and status
- Sync membership with partner
- Actions: Activate, Expire, Cancel
    """,
    'author': 'Your Name',
    'website': 'https://yourcompany.com',
    'category': 'Membership',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'subscription_package',
    ],
    'data': [
        'views/res_members_views.xml',
        'data/ir_sequence.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
