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

    
    # def _preparar_factura(self, proveedor, origin,purchase_id):
    #     """
    #     Prepara el diccionario de datos para crear la nueva factura
    # """
    #     return {
    #         'partner_id':proveedor,
    #         #'x_cuenta_analitica':cuenta_analitica,
    #         'origin':origin,
    #         'purchase_id':[(1,purchase_id)],#agregado hoy
    #         'type':'in_invoice',#agregado hoy
    #         }

    @api.model
    def create(self,vals):
        if vals.get('requisition_id'):
            purchase_ids = self.env['purchase.order'].search([('requisition_id','=',vals.get('requisition_id'))])
            for po_id in purchase_ids:
                if vals.get('partner_id') == po_id.partner_id.id:
                    raise UserError(_('RFQ is available for this purchase agreement for the same vendor'))
        return super(PurchaseOrder, self).create(vals)


    # def _preparar_linea_factura(self, factura,linea):
    #     """
    #     Prepara el diccionario de datos para crear las líneas de la nueva orden
    # """
    #     return {
    #     'invoice_id':factura.id,
    #     'product_id':linea.product_id.id,
    #     'name':linea.name,
    #     'origin':factura.name,
    #     'account_id':linea.product_id.categ_id.property_account_income_categ_id.id,
    #     'price_unit': linea.price_unit,
    #     'uom_id': linea.product_id.uom_id.id,
    #     'type':'in_invoice',
    #     'quantity':linea.product_qty,
    #     'purchase_id':[(4,factura.purchase_id.id)],
    #     'invoice_line_tax_ids':[(6,0,linea.product_id.supplier_taxes_id.ids)],
    #     'account_analytic_id':linea.account_analytic_id.id,

    #     # 'invoice_id':factura.id,
    #     # 'product_id':linea.product_id.id,
    #     # 'name':linea.name,
    #     # 'origin':factura.name,
    #     # 'account_id':linea.product_id.categ_id.property_account_income_categ_id.id,
    #     # 'price_unit': linea.price_unit,
    #     # 'uom_id': linea.product_id.uom_id.id,
    #     # 'type':'in_invoice',
    #     #'account_id': 40,
       
    #     }

    

    @api.multi
    def write(self, vals):
        context = self._context # para saber que usuario esta en sesion
        current_uid = context.get('uid')
        user = self.env['res.users'].search([('id','=',current_uid)])
        group= self.env['res.groups'].search([('name','=','validacion_director'),('users','=',user.id)]) 
        # identifico que usuario esta en sesion y que si ese usuari pertenece al grupo de validacion director
        if vals.get('partner_id') or vals.get('requisition_id'):
            purchase_ids = self.env['purchase.order'].search([('requisition_id', '=', vals.get('requisition_id'))])
            for po_id in purchase_ids:
                if vals.get('partner_id') == po_id.partner_id.id:
                    raise UserError(_('RFQ is available for this purchase agreement for the same vendor'))
        print("imprimiendo vals de purchase") 
        print(vals)
        keys=vals.keys()
        values=vals.values()
        print(keys)
        print(values)
        dom=[]
        if (('state' in keys)& ('purchase' in values)): # pregunto si state esta en lso campos que han cambiado de estod y que si values esta purchase

            if(group): 
                print("creando purchase")                  
                vals['invoice_count']=1     # este campo es para que en el modelo de purchase se vea que exist las factura. dado que en este campo lleva el conteo de facturas     
                #vals['invoice_ids']= [(0, 0,self._preparar_factura(self.partner_id.id, self.name,self.id))] #agregado hoy
                purchase_actual=super(PurchaseOrder, self).write(vals) #se crea la purchase order
                print(vals)               
                print("la self su estado es =  purchase")
                #factura_obj = self.env['account.invoice']
                print("factura data")
                print(self.name)
                #factura_data = self._preparar_factura(self.partner_id.id, self.name)
                print("hola")
                #factura_crear = factura_obj.create(factura_data) # se crea la factura
                print("se creo la factura")
                # for valor in self.order_line:
                #     linea_obj = self.env['account.invoice.line']
                #     linea_data = self._preparar_linea_factura(self.invoice_ids, valor)
                #     linea_crear = linea_obj.create(linea_data) #se crea ñla linea de la factura
                    #return super(PurchaseOrder, self).write(vals)
                #factura_crear.type='in_invoice'
                print("id de purchase")
                print(self.id)
                #print(purchase_actual.id)
                #print(factura_crear.id)
                #factura_crear.purchase_id=self.id
                print(purchase_actual)
                return purchase_actual
            else:
                print("creando purchase")            
                purchase_actual=super(PurchaseOrder, self).write(vals)           

                return purchase_actual
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

