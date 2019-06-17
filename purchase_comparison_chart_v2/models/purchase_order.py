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
    def _preparar_factura(self, proveedor, origin):
        """
        Prepara el diccionario de datos para crear la nueva factura
    """
        return {
            'partner_id':proveedor,
            #'x_cuenta_analitica':cuenta_analitica,
            'origin':origin,
            }

    @api.model
    def create(self,vals):
        if vals.get('requisition_id'):
            purchase_ids = self.env['purchase.order'].search([('requisition_id','=',vals.get('requisition_id'))])
            for po_id in purchase_ids:
                if vals.get('partner_id') == po_id.partner_id.id:
                    raise UserError(_('RFQ is available for this purchase agreement for the same vendor'))
        return super(PurchaseOrder, self).create(vals)


    def _preparar_linea_factura(self, factura,linea):
        """
        Prepara el diccionario de datos para crear las líneas de la nueva orden
    """
        return {
        'invoice_id':factura.id,
        'product_id':linea.product_id.id,
        'name':linea.name,
        'origin':factura.name,
        'account_id':linea.product_id.categ_id.property_account_income_categ_id.id,
        'price_unit': linea.price_unit,
        'uom_id': linea.product_id.uom_id.id,
        'type':'in_invoice',
        #'account_id': 40,
       
        }

    @api.multi
    def write(self, vals):
        context = self._context # para saber que usuario esta en sesion
        current_uid = context.get('uid')
        user = self.env['res.users'].search([('id','=',current_uid)])
        group= self.env['res.groups'].search([('name','=','validacion_director'),('users','=',user.id)]) 
        #
        if vals.get('partner_id') or vals.get('requisition_id'):
            purchase_ids = self.env['purchase.order'].search([('requisition_id', '=', vals.get('requisition_id'))])
            for po_id in purchase_ids:
                if vals.get('partner_id') == po_id.partner_id.id:
                    raise UserError(_('RFQ is available for this purchase agreement for the same vendor'))
        print("creando purchase")            
        purchase_actual=super(PurchaseOrder, self).write(vals)                   
        keys=vals.keys()
        values=vals.values()
        print(keys)
        print(values)
        if (('state' in keys)& ('purchase' in values)):
            if(group):                
                print("la self su estado es =  purchase")
                factura_obj = self.env['account.invoice']
                print("factura data")
                print(self.name)
                factura_data = self._preparar_factura(self.partner_id.id, self.name)
                print("hola")
                factura_crear = factura_obj.create(factura_data)
                print("se creo la factura")
                for valor in self.order_line:
                    linea_obj = self.env['account.invoice.line']
                    linea_data = self._preparar_linea_factura(factura_crear, valor)
                    linea_crear = linea_obj.create(linea_data)
                    #return super(PurchaseOrder, self).write(vals)
                factura_crear.type='in_invoice'
                return purchase_actual
        return purchase_actual   #super(PurchaseOrder, self).write(vals)

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