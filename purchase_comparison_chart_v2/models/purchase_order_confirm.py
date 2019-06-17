# -*- coding: utf-8 -*-
from odoo import models, api, _
from odoo.exceptions import UserError
from odoo.addons.website.models.website import slugify

class PurchaseOrderCompareConfirm(models.TransientModel):
    """
    This wizard will confirm the all the selected draft invoices
    """

    _name = "purchase.order.compare.confirm"
    _description = "Confirm for compare purchase order"

#     @api.multi
#     def compare_purchase_orders(self):
#         context = dict(self._context or {})
#         active_ids = context.get('active_ids', []) or []
# 
#         purchase_orders = self.env['purchase.order'].browse(active_ids)
#         if len(purchase_orders) == 0:
#             raise UserError(_('No RFQ available for compare. Please add some RFQ to compare'))
#         purchase_orders = self.env['purchase.order'].search([('id', 'in', active_ids),('state','=', 'draft')])
# 
#         if not purchase_orders:
#             raise UserError(_('All RFQs are processed. Please create mew quotation'))
#         base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].get_param('web.base.url')
# 
#         list_id = False
#         for record in purchase_orders:
#             # print (list_id)
#             # print (list_id,'list')
#             # print (record.product_list_id,'product')
#             # if not list_id == False or list_id !=  record.product_list_id:
#             #     raise UserError(_('Can not compare different product lists'))
#             list_id = record.product_list_id
#         redirect_url = "purchase_comparison_chart/purchase_comparison_product_list/%s" % (slugify(list_id.id))
#         
#         return {
#             'type': 'ir.actions.act_url',
#             'name': "Purchase Comparison Chart",
#             'target': 'self',
#             'url':redirect_url
#         }