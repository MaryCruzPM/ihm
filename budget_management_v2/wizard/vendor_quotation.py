from odoo import api, fields, models
from collections import defaultdict



class VendorQuotation(models.TransientModel):
    _name="vendor.quotation"
    
    vendor_ids= fields.Many2many("res.partner",string='Vendors')
    
    @api.multi
    def confirm_vendor(self):
        active_id = self.env.context.get('active_id')
        print(self)
        
        active_id = self.env['product.list'].search([('id','=',active_id)])
        seller_by_product_mxn = defaultdict(set)
        seller_by_product_usd = defaultdict(set)
        seller_products_mxn = defaultdict(set)
        seller_products_usd = defaultdict(set)
        usd = []
        mxn = []
        usd_seller = []
        mxn_seller = []
        print (self)
        
        for record in active_id.product_list_ids:
#             print (record.supplier_id,record.product.seller_ids)
            
            if record.supplier_id.id != False:
                if record.supplier_id.currency_id.name == 'MXN':
                    seller_by_product_mxn[record.supplier_id.name.id].add(record.product.id)
                    mxn.append(record.supplier_id.currency_id.id)
                    print('PROVEEDOR PREFERIDO CON MXN',seller_by_product_mxn)
                elif record.supplier_id.currency_id.name == 'USD':
                    seller_by_product_usd[record.supplier_id.name.id].add(record.product.id)
                    usd.append(record.supplier_id.currency_id.id)
                    print('PROVEEDOR PREFERIDO CON USD',seller_by_product_usd)
                NotImplementedError
            else:
                for vendor in self.vendor_ids:
                    print (vendor,vendor.currency_id.name)
                    if vendor.currency_id.name == 'MXN':
                        seller_products_mxn[vendor.id].add(record.product.id)
                        mxn_seller.append(vendor.currency_id.id)
                        print('PROVEEDORES MXN',seller_products_mxn)
                    elif vendor.currency_id.name == 'USD':
                        seller_products_usd[vendor.id].add(record.product.id)
                        usd_seller.append(vendor.currency_id.id)
                        print('PROVEEDORES USD',seller_products_usd)
                     
        for seller_mxn in seller_by_product_mxn.items():
            print('FOR PROVEEDOR PREFERIDO MXN',seller_mxn)
            self.purchase_order(seller_mxn[0],seller_mxn[1],mxn[0])
 
        for seller_usd in seller_by_product_usd.items():
            print('FOR PROVEEDOR PREFERIDO MXN',seller_usd)
            self.purchase_order(seller_usd[0],seller_usd[1],usd[0])
 
        for vendor_mxn in seller_products_mxn.items():
            print('FOR PROVEEDORES MXN',vendor_mxn)
            print('FOR PROVEEDORES MXN',mxn_seller)
            self.purchase_order(vendor_mxn[0],vendor_mxn[1],mxn_seller[0])
 
        for vendor_usd in seller_products_usd.items():
            print('FOR PROVEEDORES USD',vendor_usd)
            print('FOR PROVEEDORES USD',usd_seller)
            self.purchase_order(vendor_usd[0],vendor_usd[1],usd_seller[0])

    def purchase_order(self,seller,producto,currency_id):
        supplier = self.env['res.partner'].browse(seller)
        active_id = self.env.context.get('active_id')
        active_id = self.env['product.list'].search([('id','=',active_id)])
        proyecto_id = active_id.project_id
        print (self,"hgfhjvhfhjjfhj")
        vals = {
            'date_order':fields.Datetime.now(),
            'x_cuenta_analitica_id':proyecto_id.analytic_account_id.id,
            'partner_id':supplier.id,
            'currency_id':currency_id,
            'product_list_id':active_id.id
        }
        print('purchase -<<<<<<',str(vals))
        res = self.env['purchase.order'].create(vals)

        for products in producto:
            product = self.env['product.product'].browse(products)
            
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
                'price_unit':product.standard_price
            }
            print(str(vals_order_line))
            res_line = self.env['purchase.order.line'].create(vals_order_line)
        r = active_id.pruchase_order_id
        r = res
        active_id.field_bool = True
        active_id.write({'is_locked':True})
        active_id.state = 'purchase'
        return r, res_line
