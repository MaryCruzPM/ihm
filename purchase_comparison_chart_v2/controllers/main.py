# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.addons import purchase


class ValidateBid(http.Controller):

    @http.route(['/purchase_comparison_chart/purchase_comparison/<model("purchase.requisition"):purchase_requisition_id>'], type='http', auth='public', website=True)
    def purchase_comparison(self, purchase_requisition_id, **post):
        supplier_ids = []; product_ids = []; values = []; amt = []; number = []; supplier_id = []
        counts = 1
        req_product_ids = []
        for line in purchase_requisition_id.line_ids:
            req_product_ids.append(line.product_id.id)
        for record in request.env['purchase.order'].sudo().search([('requisition_id', '=', purchase_requisition_id.id),('state','=', 'draft')]):
            # Append supplier
            supplier_ids.append({'supplier_id':record.partner_id.id, 'sname':record.partner_id.name})
            supplier_id.append(record.partner_id.id)
            number.append(counts)
            # Append Products and quantity
            counts += 1
            for line in record.order_line:
                if values:
                    if line.product_id.id not in product_ids:
                        product_ids.append(line.product_id.id)
                        values.append({'product_id':line.product_id.id, 'product_name':line.product_id.name, 'price':"{:,.2f}".format(line.price_unit), 'uom':line.product_id.uom_po_id.name, 'qty':line.product_qty})
                else:
                    product_ids.append(line.product_id.id)
                    values.append({'product_id':line.product_id.id, 'product_name':line.product_id.name, 'price':"{:,.2f}".format(line.price_unit), 'uom':line.product_id.uom_po_id.name, 'qty':line.product_qty})
        
        count = 0; supplier_amount_total = []; no_of_col = 2 ; even_number = [] ; odd_number = []
        # Append amount based on the products and supplier
        for separate_values in values:
            for suppliers in supplier_ids:
                for record in request.env['purchase.order'].sudo().search([('requisition_id', '=', purchase_requisition_id.id), ('partner_id', '=', suppliers['supplier_id']),('state','=', 'draft')]):
                    if separate_values['product_id'] in req_product_ids:
                        po_line = request.env['purchase.order.line'].search([('order_id', '=', record.id), ('product_id', '=', separate_values['product_id'])])
                        if po_line:
                            amt.append({'total_amount':"{:,.2f}".format(po_line.product_qty * po_line.price_unit), 'price':"{:,.2f}".format(po_line.price_unit), 'supplier_id':suppliers['supplier_id'], "purchase_order_id":record.id, "po_line":po_line.id})
                        else:
                            amt.append({'total_amount':'0.00', 'price':'0.00', 'supplier_id':suppliers['supplier_id'], "purchase_order_id":record.id,"po_line":po_line.id})

            min_amount=max_amount=-1
            for row in amt:
                if 'amt' in row:
                    if min_amount==-1:
                        min_amount=row['amt']
                    elif min_amount>=row['amt'] and row['amt']>0:
                        min_amount=row['amt']
                    if max_amount==-1:
                        max_amount=row['amt']
                    elif max_amount<=row['amt'] and row['amt']>0:
                        max_amount=row['amt']
           
            values[count]['amt'] = amt
            values[count]['min_amount'] = "{:,.2f}".format(min_amount)
            values[count]['max_amount'] = "{:,.2f}".format(max_amount)
            count += 1
            amt = []
        # Generate number to create rows and columns
        total_supplier = len(number)
        if total_supplier >= 2:
            increase_by_supplier = total_supplier * no_of_col
        else:
            increase_by_supplier = no_of_col
        if total_supplier > 1:
            total_no = range(1, increase_by_supplier + 1)
            supplier_amount_total_1 = list(range(1, increase_by_supplier + 1))
        else:
            total_no = range(1, increase_by_supplier)
            supplier_amount_total_1 = list(range(1, increase_by_supplier))
        for c_number in total_no:
            if c_number % 2 == 0:
                even_number.append(c_number)
            else:
                odd_number.append(c_number)
        for record in request.env['purchase.order'].sudo().search([('requisition_id', '=', purchase_requisition_id.id),('state','=', 'draft')]):
            supplier_amount_total.append(record.amount_total)
        # Update the amount in even number position
        tcount = 1    
        for i in even_number:        
            supplier_amount_total_1[i - 1] = "{:,.2f}".format(supplier_amount_total[tcount - 1])
            tcount += 1
        # Update the supplier id in odd number position
        scount = 1
        for odd_no in odd_number:
            for total in total_no:
                if total == odd_no:                  
                    supplier_amount_total_1[odd_no - 1] = "{:,.2f}".format(supplier_id[scount - 1])
                    scount += 1
        return request.render('purchase_comparison_chart_v2.purchase_comparison', {'data': values, 'supplier':supplier_ids, 'purchase_requisition_id':purchase_requisition_id,
                                                               'number':number, 'to_no':total_no, 'column_no':even_number, 'supplier_amount_total':supplier_amount_total,
                                                                'supplier_amount_total_1':supplier_amount_total_1, 'odd_number':odd_number})
    
    @http.route(['/create_purchase_order'], type='http', auth="public", website=True, csrf=False)
    def create_po(self, **post):
        purchases = []
        po_lines = []
        for key in post:
            if not key == "box":
                purchase_id = int((post[key].split('_')[2]))
                purchase_line_id = int((post[key].split('_')[3]))
                purchases.append(purchase_id)
                po_lines.append(purchase_line_id)
        purchase_order_id = request.env['purchase.order'].sudo().search([('id', 'in', purchases),('state','=', 'draft')])  
        purchase_order_id_product_list = request.env['purchase.order'].sudo().search([('id', 'in', purchases),('state','=', 'draft'),('product_list_id','!=','null')])  
        cancel_purchase_order_ids = False
        print(purchase_order_id)
        print(purchase_order_id_product_list)
        if purchase_order_id_product_list:
            print("hola product_list_id")
            for res in purchase_order_id_product_list: 
                print(purchases)
                
                print("otro")                
                cancel_purchase_order_ids =  request.env['purchase.order'].sudo().search([('id', 'not in',purchases),('product_list_id', '=', res.product_list_id.id),('state','=', 'draft')])
                print("true cancel busqueda de puchase")
                print (res.id)
                print (res.requisition_id.name)

            if cancel_purchase_order_ids:
                print("cancelando")
                for can in cancel_purchase_order_ids:
                    can.button_cancel()
            
            for pro in purchase_order_id_product_list:    
                purchase_order_line = request.env['purchase.order.line'].sudo().search([('order_id.product_list_id', '=', pro.product_list_id.id),('id','in',po_lines),('order_id.state','=', 'draft')])
                for lines in pro.order_line:
                    if lines.id not in po_lines :
                        lines.unlink()  

            purchase_ids = False
            for pr in purchase_order_id_product_list:
                purchase_ids = request.env['purchase.order'].sudo().search([('id','in',purchases),'|', ('product_list_id', '=', pr.product_list_id.id),('product_list_id', '=', pr.product_list_id.id),('state','=',"draft")])
            
            list_id = 0
            requisition_id = False
            if purchase_ids:
                group=False
                for loop in purchase_ids:
                    
                    requisition_id = loop.requisition_id
                    list_id = loop.product_list_id
                    loop.button_confirm()


            if list_id:

                
                return request.render('purchase_comparison_chart_v2.purchase_comparison_list_confirm', {'list_id':list_id})
            else:
                return request.render('purchase_comparison_chart_v2.purchase_comparison_confirm', {'product_list_id':product_list_id})






        else:
     #***********************************************************************************************           
            for res in purchase_order_id: 
                print(purchases)
                
                print("otro")                
                cancel_purchase_order_ids =  request.env['purchase.order'].sudo().search([('id', 'not in',purchases),('requisition_id', '=', res.requisition_id.id),('state','=', 'draft')])
                print("true cancel busqueda de puchase")
                print (res.id)
                print (res.requisition_id.name)
                #print(cancel_purchase_order_ids.name)

            if cancel_purchase_order_ids:
                print("cancelando")
                for can in cancel_purchase_order_ids:
                    can.button_cancel()
            
            for pro in purchase_order_id:    
                purchase_order_line = request.env['purchase.order.line'].sudo().search([('order_id.requisition_id', '=', pro.requisition_id.id),('id','in',po_lines),('order_id.state','=', 'draft')])
                for lines in pro.order_line:
                    if lines.id not in po_lines :
                        lines.unlink()  

            purchase_ids = False
            for pr in purchase_order_id:
                purchase_ids = request.env['purchase.order'].sudo().search([('id','in',purchases),'|', ('requisition_id', '=', pr.requisition_id.id),('product_list_id', '=', pr.product_list_id.id),('state','=',"draft")])
            
            list_id = 0
            requisition_id = False
            if purchase_ids:
                for loop in purchase_ids:
                    requisition_id = loop.requisition_id
                    list_id = loop.product_list_id
                    loop.button_confirm()

            if list_id:

                
                return request.render('purchase_comparison_chart_v2.purchase_comparison_list_confirm', {'list_id':list_id})
            else:
                return request.render('purchase_comparison_chart_v2.purchase_comparison_confirm', {'requisition_id':requisition_id})

    #*********************************************************************

    @http.route(['/purchase_comparison_chart/purchase_comparison_product_list/<model("product.list"):list_id>'], type='http', auth='public', website=True)
    def purchase_comparison_list(self, list_id, **post):
        supplier_ids = []; product_ids = []; values = []; amt = []; number = []; supplier_id = []
        counts = 1
        req_product_ids = []
        for line in list_id.product_list_ids:
            req_product_ids.append(line.product.id)
        for record in request.env['purchase.order'].sudo().search([('product_list_id', '=', list_id.id),('state','=', 'draft')]):
            # Append supplier
            supplier_ids.append({'supplier_id':record.partner_id.id, 'sname':record.partner_id.name})
            supplier_id.append(record.partner_id.id)
            number.append(counts)
            # Append Products and quantity
            counts += 1

            for line in record.order_line:
                for res in request.env['qty.budget'].sudo().search([('name', '=', line.product_id.id),('project_id.analytic_account_id', '=', line.order_id.x_cuenta_analitica_id.id)]):
                    for exe in request.env['product.list'].sudo().search([('product_list_ids.product', '=', line.product_id.id),('project_id.analytic_account_id', '=',line.order_id.x_cuenta_analitica_id.id)]):
                        for product_list in exe.product_list_ids:
                            if values:
                                if line.product_id.id not in product_ids:
                                    product_ids.append(line.product_id.id)
                                    values.append({'product_id':line.product_id.id, 
                                                   'product_name':line.product_id.name,
                                                    'price':"{:,.2f}".format(line.price_unit),
                                                    'uom':line.product_id.uom_po_id.name,
                                                    'qty':"{:,.2f}".format(line.product_qty),
                                                    'planned_qty':"{:,.2f}".format(res.cantidad_total),
                                                    'planned_bud':"{:,.2f}".format(res.qty),
                                                    'exe_qty':"{:,.2f}".format(res.executed),
                                                    'exe_bud':"{:,.2f}".format(res.executed_cost),
                                                    'new_exe_qty':"{:,.2f}".format(line.product_qty + res.executed)
                                                    })
                            else:
                                product_ids.append(line.product_id.id)
                                values.append({'product_id':line.product_id.id, 
                                               'product_name':line.product_id.name, 
                                               'price':"{:,.2f}".format(line.price_unit), 
                                               'uom':line.product_id.uom_po_id.name, 
                                                'qty':"{:,.2f}".format(line.product_qty),
                                                'planned_qty':"{:,.2f}".format(res.cantidad_total),
                                                'planned_bud':"{:,.2f}".format(res.qty),
                                                'exe_qty':"{:,.2f}".format(res.executed),
                                                'exe_bud':"{:,.2f}".format(res.executed_cost),
                                                'new_exe_qty':"{:,.2f}".format(line.product_qty + res.executed)
                                               })
        
        count = 0; supplier_amount_total = []; no_of_col = 2 ; even_number = [] ; odd_number = []
        
        # Append amount based on the products and supplier
        for separate_values in values:
            for suppliers in supplier_ids:
                for record in request.env['purchase.order'].sudo().search([('product_list_id', '=', list_id.id), ('partner_id', '=', suppliers['supplier_id']),('state','=', 'draft')]):
                    if separate_values['product_id'] in req_product_ids:
                        po_line = request.env['purchase.order.line'].search([('order_id', '=', record.id), ('product_id', '=', separate_values['product_id'])])
                        if po_line:
                            amt.append({'total_amount':"{:,.2f}".format(po_line.product_qty * po_line.price_unit), 'price':"{:,.2f}".format(po_line.price_unit), 'amt':po_line.price_unit, 'supplier_id':suppliers['supplier_id'], "purchase_order_id":record.id, "po_line":po_line.id, "product_id":separate_values['product_id']})
                            
                        else:
                            amt.append({'total_amount':'0.00', 'price':'0.00', 'supplier_id':suppliers['supplier_id'], "purchase_order_id":record.id,"po_line":po_line.id, "product_id":separate_values['product_id']})
            

            min_amount=max_amount=-1
            for row in amt:
                if 'amt' in row:
                    if min_amount==-1:
                        min_amount=row['amt']
                    elif min_amount>=row['amt'] and row['amt']>0:
                        min_amount=row['amt']
                    if max_amount==-1:
                        max_amount=row['amt']
                    elif max_amount<=row['amt'] and row['amt']>0:
                        max_amount=row['amt']
           
            
            values[count]['amt'] = amt
            values[count]['min_amount'] = "{:,.2f}".format(min_amount)
            values[count]['max_amount'] = "{:,.2f}".format(max_amount)
            count += 1
            amt = []
        # Generate number to create rows and columns
        total_supplier = len(number)
        if total_supplier >= 2:
            increase_by_supplier = total_supplier * no_of_col
        else:
            increase_by_supplier = no_of_col
        if total_supplier > 1:
            total_no = range(1, increase_by_supplier + 1)
            supplier_amount_total_1 = list(range(1, increase_by_supplier + 1))
        else:
            total_no = range(1, increase_by_supplier)
            supplier_amount_total_1 = list(range(1, increase_by_supplier))
        for c_number in total_no:
            if c_number % 2 == 0:
                even_number.append(c_number)
            else:
                odd_number.append(c_number)
        for record in request.env['purchase.order'].sudo().search([('product_list_id', '=', list_id.id),('state','=', 'draft')]):
            supplier_amount_total.append(record.amount_total)
        # Update the amount in even number position
        tcount = 1    
        for i in even_number:        
            supplier_amount_total_1[i - 1] = "{:,.2f}".format(supplier_amount_total[tcount - 1])
            tcount += 1
        # Update the supplier id in odd number position
        scount = 1
        for odd_no in odd_number:
            for total in total_no:
                if total == odd_no:                  
                    supplier_amount_total_1[odd_no - 1] = "{:,.2f}".format(supplier_id[scount - 1])
                    scount += 1
        return request.render('purchase_comparison_chart_v2.purchase_comparison_list', {'po':0,'data':values, 'supplier':supplier_ids, 'list_id':list_id, 
                                                               'number':number, 'to_no':total_no, 'column_no':even_number, 'supplier_amount_total':supplier_amount_total,
                                                                'supplier_amount_total_1':supplier_amount_total_1, 'odd_number':odd_number})


        

    @http.route(['/purchase_comparison_chart/purchase_comparison_product_list/po/<string:list>'], type='http', auth='public', website=True)
    def purchase_comparison_po_list(self, list, **post):
        supplier_ids = []; product_ids = []; values = []; amt = []; number = []; supplier_id = []
        counts = 1
        req_product_ids = []
        
        for line in request.env['purchase.order'].sudo().search([('id', 'in', list.split('-'))]):
            for row in line.order_line:
                req_product_ids.append(row.product_id.id)
            
        for record in request.env['purchase.order'].sudo().search([('id', 'in', list.split('-')),('state','=', 'draft')]):
            # Append supplier
            supplier_ids.append({'supplier_id':record.partner_id.id, 'sname':record.partner_id.name})
            supplier_id.append(record.partner_id.id)
            number.append(counts)
            # Append Products and quantity
            counts += 1

            for line in record.order_line:
                if values:
                    if line.product_id.id not in product_ids:
                        product_ids.append(line.product_id.id)
                        values.append({'product_id':line.product_id.id, 
                                       'product_name':line.product_id.name,
                                        'price':"{:,.2f}".format(line.price_unit),
                                        'uom':line.product_id.uom_po_id.name,
                                        'qty':"{:,.2f}".format(line.product_qty),
#                                         'planned_qty':"{:,.2f}".format(0),
#                                         'planned_bud':"{:,.2f}".format(0),
                                        'exe_qty':"{:,.2f}".format(0),
                                        'exe_bud':"{:,.2f}".format(0),
                                        'new_exe_qty':"{:,.2f}".format(0)
                                        })
                else:
                    product_ids.append(line.product_id.id)
                    values.append({'product_id':line.product_id.id, 
                                   'product_name':line.product_id.name, 
                                   'price':"{:,.2f}".format(line.price_unit), 
                                   'uom':line.product_id.uom_po_id.name, 
                                    'qty':"{:,.2f}".format(line.product_qty),
#                                     'planned_qty':"{:,.2f}".format(0),
#                                     'planned_bud':"{:,.2f}".format(0),
                                    'exe_qty':"{:,.2f}".format(0),
                                    'exe_bud':"{:,.2f}".format(0),
                                    'new_exe_qty':"{:,.2f}".format(0)
                                   })

        count = 0; supplier_amount_total = []; no_of_col = 2 ; even_number = [] ; odd_number = []
        # Append amount based on the products and supplier
        for separate_values in values:
            for suppliers in supplier_ids:
                for record in request.env['purchase.order'].sudo().search([('id', 'in', list.split('-')), ('partner_id', '=', suppliers['supplier_id']),('state','=', 'draft')]):
                    if separate_values['product_id'] in req_product_ids:
                        po_line = request.env['purchase.order.line'].search([('order_id', '=', record.id), ('product_id', '=', separate_values['product_id'])])
                        if po_line:
                            amt.append({'total_amount':"{:,.2f}".format(po_line.product_qty * po_line.price_unit), 'price':"{:,.2f}".format(po_line.price_unit), 'amt':po_line.price_unit, 'supplier_id':suppliers['supplier_id'], "purchase_order_id":record.id, "po_line":po_line.id, "product_id":separate_values['product_id']})
                            
                        else:
                            amt.append({'total_amount':'0.00', 'price':'0.00', 'supplier_id':suppliers['supplier_id'], "purchase_order_id":record.id,"po_line":po_line.id, "product_id":separate_values['product_id']})
            
            
            min_amount=max_amount=-1
            for row in amt:
                if 'amt' in row:
                    if min_amount==-1:
                        min_amount=row['amt']
                    elif min_amount>=row['amt'] and row['amt']>0:
                        min_amount=row['amt']
                    if max_amount==-1:
                        max_amount=row['amt']
                    elif max_amount<=row['amt'] and row['amt']>0:
                        max_amount=row['amt']
           
            values[count]['amt'] = amt
            values[count]['min_amount'] = "{:,.2f}".format(min_amount)
            values[count]['max_amount'] = "{:,.2f}".format(max_amount)
            count += 1
            amt = []
        # Generate number to create rows and columns
        
        total_supplier = len(number)
        if total_supplier >= 2:
            increase_by_supplier = total_supplier * no_of_col
        else:
            increase_by_supplier = no_of_col
        
        if total_supplier > 1:
            total_no = range(1, increase_by_supplier + 1)
            list_new=[]
            for val_new in range(1, increase_by_supplier + 1):
                list_new.append(val_new)            
            supplier_amount_total_1 = list_new
        else:
            total_no = range(1, increase_by_supplier)
            list_new=[]
            for val_new in range(1, increase_by_supplier):
                list_new.append(val_new)            
            supplier_amount_total_1 = list_new
            
        for c_number in total_no:
            if c_number % 2 == 0:
                even_number.append(c_number)
            else:
                odd_number.append(c_number)
                
        for record in request.env['purchase.order'].sudo().search([('id', 'in', list.split('-')),('state','=', 'draft')]):
            supplier_amount_total.append(record.amount_total)
        # Update the amount in even number position
        tcount = 1    
        for i in even_number:        
            supplier_amount_total_1[i - 1] = "{:,.2f}".format(supplier_amount_total[tcount - 1])
            tcount += 1
        # Update the supplier id in odd number position
        scount = 1
        for odd_no in odd_number:
            for total in total_no:
                if total == odd_no:                  
                    supplier_amount_total_1[odd_no - 1] = "{:,.2f}".format(supplier_id[scount - 1])
                    scount += 1
        return request.render('purchase_comparison_chart_v2.purchase_comparison_list', {'po':1,'data':values, 'supplier':supplier_ids, 'list_id':False, 
                                                               'number':number, 'to_no':total_no, 'column_no':even_number, 'supplier_amount_total':supplier_amount_total,
                                                                'supplier_amount_total_1':supplier_amount_total_1, 'odd_number':odd_number})