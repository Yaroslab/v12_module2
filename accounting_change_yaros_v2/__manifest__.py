# -*- coding: utf-8 -*-

{
    'name': 'Cambiar cuenta corriente facturas',
    'version': '2.0',
    'category': 'Account',
    'author': 'YarosLab SAC',
    'description': """
    Agrega una relación entre el diario y la moneda que van a determinar la cuenta por cobrar o
    pagar a utilizar en los documentos de venta o compra.
""",
    'depends': ['account', 'account_cancel', 'sale_management', 'purchase', 'l10n_pe'],
    'data': [
        'security/ir.model.access.csv',
        'views/trees.xml',
        'views/actions.xml',
        'views/menus.xml'
    ],
    'installable': True,
    'website': 'https://www.yaroscloud.com',
    'price': 0.00,
    'license': 'AGPL-3',
}
