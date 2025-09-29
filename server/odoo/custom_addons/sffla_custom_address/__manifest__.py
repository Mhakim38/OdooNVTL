{
    "name": "SFFLA Custom Address",
    "version": "17.0.1.0.0",
    "summary": "Use a single full address field instead of structured fields",
    "description": """
        Customization of Partner model:
        - Removes street, city, state, zip, country fields from form
        - Adds one text field for full address
    """,
    "author": "Your Name/Company",
    "website": "https://yourcompany.com",
    "category": "Customizations",
    "depends": ["base"],
    "data": [
        "views/custom_address_view.xml",
    ],
    "installable": True,
    "application": False,
    "license": "LGPL-3",
}
