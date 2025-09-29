# -*- coding: utf-8 -*-
{
    "name": "SFFLA Company Circulars",
    "version": "17.0.1.0.0",
    "summary": "Create, publish, and track acknowledgements of internal circulars.",
    "author": "Your Company",
    "license": "LGPL-3",
    "category": "Human Resources",
    "depends": ["mail", "hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/circular_views.xml",
        "views/import_circular_files_views.xml",
    ],
    "installable": True,
    "application": True,
}
