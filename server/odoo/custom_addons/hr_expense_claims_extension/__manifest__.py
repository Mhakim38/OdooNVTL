
{
    'name': 'HANSON HR Expense Claims Extension',
    'version': '1.0',
    'summary': 'Extend HR Expenses with Sales Claims Logic',
    'depends': ['hr_expense'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_expense_views.xml',
    ],
    'installable': True,
    'application': False,
}
