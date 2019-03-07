# -*- coding: utf-8 -*-

{
    'name': 'Que su referencia del proveedor sea estructurada',
    'version': '2.0',
    'category': 'Account',
    'author': 'YarosLab SAC',
    'description': """
Que su referencia del proveedor sea estructurada
""",
    'depends': ['account_cancel'],
    'data': [
        'security/ir.model.access.csv',
        'views/forms.xml',
        'views/trees.xml',
        'views/actions.xml',
        'views/menus.xml',
        'static/src/xml/qweb_extend.xml',
    ],
    'price': 0.00,
    'installable': True,
    'license': 'AGPL-3',
    'website': 'https://www.yaroscloud.com',
}
