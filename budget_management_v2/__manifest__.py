# -*- encoding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Budget Management by Quantity',
    'version': '1.2',
    'category': 'Project',
    'summary': 'Budget Management by Quantity by using Project',
    'author':'PPTS [India] Pvt.Ltd.',
    'description': """
Budget Management by Quantity
=============================
To establish and control the quantities bought of a product category in a project.
    """,
    'depends': ['project','project_product_list','purchase','base'],
    'website': 'https://www.pptssolutions.com',
    'data': [
        'security/ir.model.access.csv',
#         'wizard/vendor_quotation.xml',
        'views/qty_budget_view.xml',
        'views/custom_project_view.xml',
        'views/purchase_order.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
