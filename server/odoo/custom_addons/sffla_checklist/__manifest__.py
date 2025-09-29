# -*- coding: utf-8 -*-
{
    'name': "SFFLA Checklist",
    'version': '17.0.1.0.0',
    'category': 'Sales/Subscription',
    'summary': "Verification checklist for Subscription Package",
    'description': """
Adds a verification checklist to the Subscription Package process.

Features:
- Checklist items in Verify stage
- Tick button to mark as Done
- Access rights for users and managers
    """,
    'author': "Your Company",
    'website': "http://www.yourcompany.com",
    'license': 'AGPL-3',
    'depends': [
        'base',
        'mail',
        'sale',
        'hr',
        'subscription_package',
        'calendar',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/verify_checklist.xml',   # load checklist view
        'views/subscription_package_interview.xml',
    ],
    'installable': True,
    'application': True,
}
