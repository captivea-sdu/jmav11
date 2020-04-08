{
    "name": "cap_import_technical",
    "version": "1.0",
    "depends": ["base","product","sale","mrp","odoo_magento_connect","cap_delivery_data", "base_import"],
    "author": "Captivea (ylb)",
    "category": "None",
    "description": """
    Module technique d'aide à l'import des données JMA dans odoo
    """,
    "qweb": [],
    "data": [
            'views/assets.xml',
            'views/magento_configure.xml',
            'data.xml'
             ],
    "demo": [],
    "test": [],
    "css":[],
    "js":[],
    "installable": True,
    "active": True,
#    'certificate': 'certificate',
}
