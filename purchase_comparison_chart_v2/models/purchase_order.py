from odoo import models, fields,api,_
from urllib.parse import urljoin
from odoo.addons.website.models.website import slugify
from odoo.exceptions import UserError
import xlwt
import base64
from datetime import datetime

from werkzeug.urls import url_encode
import werkzeug

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # state = fields.Selection([
    #     ('draft', 'RFQ'),
    #     ('sent', 'RFQ Sent'),
    #     ('to approve', 'To Approve'),
    #     ('purchase', 'Purchase Order'),
    #     ('done', 'Locked'),
    #     ('cancel', 'Cancelled')
    # ], string='Status', compute='_cambia_factura', readonly=True, index=True, copy=False, default='draft', track_visibility='onchange')
    


    # @api.one
    # @api.depends('state')
    # def _cambia_factura(self):
    #     print("entrando a validar el usuario oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooddddddmmmmmm")
    #     #print(self.state)
    #     print(self)
    #         #if (self.state == 'purchase'):   
    #     if (self.state == 'purchase'):
    #         print("purchase su estado es una orden de compra")
    #         self.action_view_invoice()               
                   

    #     else:
    #         print("no es purchase")  
    #     x_status='true'
    #     print(self.x_status)


    @api.model
    def create(self,vals):
        if vals.get('requisition_id'):
            purchase_ids = self.env['purchase.order'].search([('requisition_id','=',vals.get('requisition_id'))])
            for po_id in purchase_ids:
                if vals.get('partner_id') == po_id.partner_id.id:
                    raise UserError(_('RFQ is available for this purchase agreement for the same vendor'))
        return super(PurchaseOrder, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('partner_id') or vals.get('requisition_id'):
            purchase_ids = self.env['purchase.order'].search([('requisition_id', '=', vals.get('requisition_id'))])
            for po_id in purchase_ids:
                if vals.get('partner_id') == po_id.partner_id.id:
                    raise UserError(_('RFQ is available for this purchase agreement for the same vendor'))
        return super(PurchaseOrder, self).write(vals)

    @api.multi
    def compare_purchase_orders(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        purchase_orders_id = self.env['purchase.order'].search([("id","in",active_ids)])
        vendor_list = []
        for rec in purchase_orders_id:
            if not rec.partner_id in vendor_list:
                vendor_list.append(rec.partner_id)
            else:                
                raise UserError(_('Same Vendors should not be selected, Please select different vendors for Purchase Comparison'))
       
        purchase_orders = self.env['purchase.order'].browse(self.ids)
        if len(purchase_orders) == 0:
            raise UserError(_('No RFQ available for compare. Please add some RFQ to compare'))
        purchase_orders = self.env['purchase.order'].search([('id', 'in', self.ids),('state','=', 'draft')])

        if not purchase_orders:
            raise UserError(_('All RFQs are processed. Please create new quotation'))
        base_url = '/' if self.env.context.get('relative_url') else self.env['ir.config_parameter'].get_param('web.base.url')

        list_id = False
        for record in purchase_orders:
            list_id = record.product_list_id
        if not list_id:
            redirect_url = "purchase_comparison_chart/purchase_comparison_product_list/po/%s" % (slugify(active_ids))
        else:
            redirect_url = "purchase_comparison_chart/purchase_comparison_product_list/%s" % (slugify(list_id.id))
        
        return {
            'type': 'ir.actions.act_url',
            'name': "Purchase Comparison Chart",
            'target': 'self',
            'url':redirect_url
        }



    # x_status = fields.Char(string='x_status',compute='_cambia_factura')