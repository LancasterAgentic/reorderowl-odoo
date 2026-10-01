{
    "name": "ReorderOwl Readiness",
    "version": "18.0.1.0.0",
    "summary": "Check that your products, vendors and lead times are ready for reorder planning",
    "description": "Read-only report of the data that weakens reorder suggestions, plus the "
                   "connection details ReorderOwl needs. Sends no data anywhere.",
    "category": "Inventory/Purchase",
    "author": "Lancaster Agentic",
    "website": "https://reorderowl.com",
    "license": "LGPL-3",
    "depends": ["purchase_stock"],
    "data": [
        "security/ir.model.access.csv",
        "views/readiness_views.xml",
    ],
    "images": ["static/description/banner.png"],
    "application": False,
    "installable": True,
}
