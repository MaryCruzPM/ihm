# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from odoo import models, fields,api,_
from odoo.exceptions import UserError, ValidationError

class Project(models.Model):
    _inherit = "project.project"
    
    product_qty = fields.Char("Budget Quantity")  
    product_list_ids = fields.Many2many("product.product",string="Product list",compute="_compute_product_list")
    picking_id = fields.Many2one("stock.picking.type",string="Location", domain = [('name', '=', 'Receipts')])
    user_access = fields.Selection([('yes', 'Yes'), 
                                ('no', 'No')
                                  ],compute="_compute_user_access", string="User Access")
                                  
    pagos_efectivo_ids = fields.One2many(
                                         'pagos.efectivo', 
                                         'proyecto_id', 
                                         string="Pagos en efectivo"
                                         )
    
                                         
    @api.one
    @api.model
    def _compute_cantidad_ejecutada(self):
#        total=sum(self.env['qty.budget'].search(['project_id','=',self.id]).mapped('executed_cost'))
        print("CALCULANDO TOTALIDAD")
        total=0
        #pagos=self.env['account.payment'].search([('id_numero_referencia', '=', self.id_numero_referencia.name)])
        budgets=self.env['qty.budget'].search([('project_id','=',self.id)])
        for line in budgets:
            total+=line.executed_cost
        self.cantidad_ejecutada=total
        
    @api.one
    @api.depends('pagos_efectivo_ids.importe')
    def _compute_suma_gastos(self):
        self.suma_gastos_efectivo = sum(line.importe for line in self.pagos_efectivo_ids)
    
    @api.one
    @api.depends('suma_gastos_efectivo')
    def _compute_total_total(self):
        self.total_total = self.cantidad_ejecutada + self.suma_gastos_efectivo
        
    cantidad_ejecutada=fields.Float(string="Cantidad ejecutada",compute='_compute_cantidad_ejecutada')
    suma_gastos_efectivo=fields.Float(string='Suma de gastos',
                               readonly=True, 
                               compute='_compute_suma_gastos',
                               )
    total_total=fields.Float(string='Total',
                               readonly=True, 
                               compute='_compute_total_total',
                               )
    
    @api.multi
    def _compute_user_access(self):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        #print(user.id)
        #print(user.name)
        #print("-------------------")
        for access_id in self:
            if user.id == 2 or user.id == 6 or user.id == 21 or user.id == 17 or user.id == 9:
                access_id.user_access = 'yes' 
            else:
                access_id.user_access = 'no' 
    
    @api.one
    def _compute_product_list(self):
        products_list = []
        product_list_ids_rec = self.env['qty.budget'].search([])
        for loop in product_list_ids_rec:
            products_list.append(loop.name.id)
        for line in self:
            line.product_list_ids = products_list
            print(line.product_list_ids)
   
class productList(models.Model):
    _inherit = 'product.list'
  
    @api.multi
    @api.onchange('product_list_ids')   
    def _onchange_cantidad(self):      
        cate_id = self.env['product.category'].search([])        
        for cate in cate_id:
            amount = 0.0
            for line in self.product_list_ids:
                if line.product.categ_id.id == cate.id:
                    amount += line.cantidad 
                    if (amount+line.executed) > line.budget:
                        line.status = 'over_budget' 
                    else:
                        line.status = 'available' 
                    
    @api.one
    def _display_count(self):
        for rel in self:
            count_id = self.env['purchase.order'].search([('product_list_id', '=', rel.id)])

            self.purchase_count= len(count_id)
            
            
    @api.one
    def _display_status(self):
#         if self.state =='purchase': 
#             self.status_pro ="Processed"
#         else:
#             self.status_pro ="Not Processed" 
            
        status_id = self.env['purchase.order.line'].search([
            ('order_id.product_list_id','=',self.name),
            ('order_id.x_cuenta_analitica_id','=',self.project_id.analytic_account_id.id),
            ('order_id.state','in',('purchase','cancel'))
        ])
        if status_id:
            self.status_pro ="processed"
        else:
            self.status_pro ="not_processed"   

         
            
    status_compute = fields.Boolean(compute="_compute_status",string="Line Status Check")
    purchase_count= fields.Integer(string="Purchase Count",compute="_display_count")
    status_pro = fields.Selection([('processed', "Processed"), ('not_processed', "Not Processed")],"Status",compute="_display_status",default='not_processed')  
    
    @api.multi
    def view_purchase_order(self):
        
        purchase_id = self.env['purchase.order'].search([('product_list_id', 'in', self.ids)]).ids
        action = self.env.ref('purchase.purchase_rfq').read()[0]
        if purchase_id:
            action['domain'] = [('id', 'in', purchase_id)]
            action['context'] = {'default_product_list_id': self.id}
        return action

    @api.multi
    def procesar_compras(self):
        return True
   
    @api.one
    def _compute_status(self):
        for rec in self:
            status=True
            if len(rec.product_list_ids)==0:                
                status=False
            for list in rec.product_list_ids:
                if list.status=='over_budget':
                    status=False
            rec.status_compute = status
            
    
    @api.multi
    def set_done(self):
#         for record in self.product_list_ids:
#             if record.status == 'over_budget':
#                 raise ValidationError(_('The Product Quantities not in Budget.'))
        self.state = 'done'
        self.write({'is_locked':True})

#     @api.multi
#     def is_approve(self):
#         cate_id = self.env['product.category'].search([])
#         for cate in cate_id:
#             amount = 0.0
#             executed=0
#             qty_add = self.env['qty.budget'].search([('name','=',cate.id),('project_id','=',self.project_id.id)])
#             if qty_add:
#                 for rec in self.product_list_ids:
#                     if rec.product.categ_id.id == cate.id:
#                         if executed==0:
#                             amount += rec.executed
#                             executed += rec.executed                             
#                         amount += rec.cantidad
# #                 if amount > qty_add.qty:
# #                     qty_add.qty = amount
#         
#         self._onchange_cantidad()
            
            
                    
    @api.multi
    def generar_orden_compra(self):
        seller_by_product_mxn = defaultdict(set)
        seller_by_product_usd = defaultdict(set)
        seller_products_mxn = defaultdict(set)
        seller_products_usd = defaultdict(set)
        usd = []
        mxn = []
        usd_seller = []
        mxn_seller = []
        print (self.product_list_ids)
        print(self.id)
        id_product_list=self.id
        #print(self.name)
        print("iniciando la requisicion")   
        for record in self.product_list_ids:
            print (record.supplier_id,record.product.seller_ids)
            print(record.product.id)
            print (record.supplier_id,record.product.seller_ids)
            if record.supplier_id.id != False:
                if record.supplier_id.currency_id.name == 'MXN':
                    seller_by_product_mxn[record.supplier_id.name.id].add(record.product.id)
                    mxn.append(record.supplier_id.currency_id.id)
                    print('PROVEEDOR PREFERIDO CON MXN',seller_by_product_mxn)
                elif record.supplier_id.currency_id.name == 'USD':
                    seller_by_product_usd[record.supplier_id.name.id].add(record.product.id)
                    usd.append(record.supplier_id.currency_id.id)
                    print('PROVEEDOR PREFERIDO CON USD',seller_by_product_usd)
                
            else:
                for vendor in record.product.seller_ids:
                    print (vendor,vendor.currency_id.name)
                    if vendor.currency_id.name == 'MXN':
                        seller_products_mxn[vendor.name.id].add(record.product.id)
                        mxn_seller.append(vendor.currency_id.id)
                        print('PROVEEDORES MXN',seller_products_mxn)
                    elif vendor.currency_id.name == 'USD':
                        seller_products_usd[vendor.name.id].add(record.product.id)
                        usd_seller.append(vendor.currency_id.id)
                        print('PROVEEDORES USD',seller_products_usd)
                    
        for seller_mxn in seller_by_product_mxn.items():
            print('FOR PROVEEDOR PREFERIDO MXN',seller_mxn)
            self.purchase_order(seller_mxn[0],seller_mxn[1],mxn[0],id_product_list)

        for seller_usd in seller_by_product_usd.items():
            print('FOR PROVEEDOR PREFERIDO MXN',seller_usd)
            self.purchase_order(seller_usd[0],seller_usd[1],usd[0],id_product_list)

        for vendor_mxn in seller_products_mxn.items():
            print('FOR PROVEEDORES MXN',vendor_mxn)
            print('FOR PROVEEDORES MXN',mxn_seller)
            self.purchase_order(vendor_mxn[0],vendor_mxn[1],mxn_seller[0],id_product_list)

        for vendor_usd in seller_products_usd.items():
            print('FOR PROVEEDORES USD',vendor_usd)
            print('FOR PROVEEDORES USD',usd_seller)
            self.purchase_order(vendor_usd[0],vendor_usd[1],usd_seller[0],id_product_list)
            
#         raise ValidationError(_('The Product Quantities not in Budget.'))
    
    
    def purchase_order(self,seller,producto,currency_id,product_list):
        supplier = self.env['res.partner'].browse(seller)
        proyecto_id = self.project_id
        if proyecto_id.picking_id:
            vals = {
                'date_order':fields.Datetime.now(),
                'x_cuenta_analitica_id':proyecto_id.analytic_account_id.id,
                'partner_id':supplier.id,
                'currency_id':currency_id,
                'product_list_id':product_list,
                'picking_type_id':proyecto_id.picking_id.id
            }
        else:
            vals = {
                'date_order':fields.Datetime.now(),
                'x_cuenta_analitica_id':proyecto_id.analytic_account_id.id,
                'partner_id':supplier.id,
                'currency_id':currency_id,
                'product_list_id':product_list,
            }
            
        print('purchase -<<<<<<',str(vals))
        res = self.env['purchase.order'].create(vals)

        for products in producto:
            product = self.env['product.product'].browse(products)
            cost=product.standard_price
            for sellers_list in product.seller_ids:
                if sellers_list.name.id==supplier.id:
                    print (sellers_list.name.name, supplier.name,'--')
                    print (sellers_list.price)
                    cost=sellers_list.price
            vals_order_line = {
                'order_id':res.id,
                'x_prioridad':product.x_seleccion,
                'product_id':product.id,
                'name':product.name,
                'account_analytic_id':proyecto_id.analytic_account_id.id,
                'x_tarea':product.x_task,
                'product_qty':product.x_qty_list,
                'date_planned':product.x_fecha_requerida,
                'product_uom':product.uom_id.id,
                'price_unit':cost,
                'taxes_id' : [( 6,0,product.supplier_taxes_id.ids)] or False
            }
            print(str(vals_order_line))
            res_line = self.env['purchase.order.line'].create(vals_order_line)
#             res_line.write({
#                 'taxes_id' : product.supplier_taxes_id.ids
#                 })
        r = self.pruchase_order_id
        r = res
        self.field_bool = True
        self.write({'is_locked':True})
        self.state = 'purchase'
        return r, res_line

class productListLine(models.Model):
    _inherit = 'product.list.line' 
     
    supplier_id = fields.Many2one('res.partner',string="Supplier")
    budget = fields.Float(compute='_compute_budget',string="Presupuesto")
    executed = fields.Float(compute="_compute_executed",string="Ejercido")
    executed_cost = fields.Float(string="Ejercido")
    status = fields.Selection([('available', "Disponible"), ('over_budget', "Sin Presupuesto")], string="Estatus")

    @api.one
    @api.depends('product')
    def _compute_budget(self):
        categ_id = self.env['qty.budget'].search([('project_id','=',self.product_list_id.project_id.id),('name','=',self.product.id)])
        if categ_id:
            self.budget = categ_id.qty
        else:
            self.budget = 0
            
    @api.one
    @api.depends('product')
    def _compute_executed(self):
#         qty_id = self.env['purchase.order.line'].search([
#             ('product_id','=',self.product.id),
#             ('order_id.x_cuenta_analitica_id','=',self.project_id.analytic_account_id.id),
#             ('order_id.state','=','purchase')
#         ])
#         total = executed_cost=0.0
#         for res in qty_id:
#             if res.state == 'purchase':
#                 total += res.product_qty
#                 executed_cost += res.price_subtotal
#         self.executed = total
#         self.executed_cost = executed_cost

        for line in self:
                qty_id = self.env['stock.picking'].search([
                    ('move_ids_without_package.product_id','=',line.product.id),
                    ('x_cuenta_analitica','=',line.project_id.analytic_account_id.id),
                    ('state','=','done')
                ])
    #             print(acc_id,"amount")
    #             print(qty_id,"stock")
                total =0.0
                for res in qty_id:
                    if res.state == 'done':
                        for reco in res.move_ids_without_package:
                            if line.product.id == reco.product_id.id:
                                total += reco.quantity_done
    #                     executed_cost += res.price_subtotal
                            line.executed = total
    #             line.executed_cost = executed_cost
                
    @api.onchange('cantidad')
    def on_change_state(self):
        if self.cantidad and self.budget:
            total_qty = self.cantidad + self.executed
            if total_qty <= self.budget:
                self.status = 'available'
            if total_qty > self.budget: 
                self.status = 'over_budget'
                
    
                
  
        
            
            
               
    
