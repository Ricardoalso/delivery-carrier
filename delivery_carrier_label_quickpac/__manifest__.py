# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'Quickpac',
    'version': '12.0.1.0.0',
    'author': 'Camptocamp',
    'maintainer': 'Camptocamp',
    'category': 'Delivery',
    'complexity': 'normal',
    'depends': [
        'base_delivery_carrier_label',
        'delivery_carrier_label_batch',
        'configuration_helper',
        'stock',
    ],
    'description': """
    """,
    'website': 'http://www.camptocamp.com/',
    'data': [
        'data/product.xml',
        'data/partner.xml',
        'data/delivery.xml',
        'views/delivery.xml',
        'views/res_config.xml',
    ],
    'external_dependencies': {
        'python': [
            'quickpac',
        ],
    },
    'installable': True,
    'license': 'AGPL-3',
    'application': True
}
