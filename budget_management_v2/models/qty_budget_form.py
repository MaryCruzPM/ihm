# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import models, fields,api,_

from odoo.exceptions import UserError, ValidationError

class QuantityBudget(models.Model):
    _name = 'qty.budget'
    _description = 'Quantity Budget'
    
    product_list_ids = fields.Many2many("product.product",string="Product list",related="project_id.product_list_ids")
    name = fields.Many2one("product.product",string="Product",required=True)
    category_id = fields.Many2one(related="name.categ_id",string="Category",store=True)
    qty = fields.Float("Quantity",required=True)
    uom_id = fields.Many2one("uom.uom",string="UOM")
    project_id = fields.Many2one("project.project",string="Project")
    cantidad_total=fields.Float(string="Presupuesto",default=0.0)
    executed = fields.Float(compute="_compute_values",string="Executed Qty")
    executed_cost = fields.Float(compute="_compute_values",string="Executed Amount")
    percentage_qty = fields.Float(compute="_compute_values",string="% Executed Qty")
    percentage_amt = fields.Float(compute="_compute_values",string="% Executed Amount")
    remaining_amt = fields.Float(compute="_compute_values",string="Remaining Amount")
    remaining_qty = fields.Float(compute="_compute_values",string="Remaining Qty")
    
 
    @api.multi
    @api.depends('name')
    def _compute_values(self):
        for line in self:
            qty_id = self.env['stock.picking'].search([
                ('move_ids_without_package.product_id','=',line.name.id),
                ('x_cuenta_analitica','=',line.project_id.analytic_account_id.id),
                ('state','=','done')
            ])
            acc_id = self.env['account.invoice'].search([
                ('purchase_id.x_cuenta_analitica_id','=',line.project_id.analytic_account_id.id),
                ('invoice_line_ids.product_id','=',line.name.id),
                ('state','in',('paid','open'))
            ])
#             print(acc_id,"amount")
#             print(qty_id,"stock")
            total =0.0
            for res in qty_id:
                if res.state == 'done':
                    for reco in res.move_ids_without_package:
                        if line.name.id == reco.product_id.id:
                            if reco.product_id.type != 'service':
                                total += reco.quantity_done
    #                     executed_cost += res.price_subtotal
                            line.executed = total
#             line.executed_cost = executed_cost
            executed_cost =0.0
            exe_qty_service = 0.0
            for ren in acc_id:
                if ren.state == 'paid':
                    for recod in ren.invoice_line_ids:
                        if recod.product_id.type != 'service':
                            if line.name.id == recod.product_id.id:
                                executed_cost += recod.price_total
                            line.executed_cost = executed_cost
                        if recod.product_id.type == 'service':  
                            if line.name.id == recod.product_id.id:
                                executed_cost += recod.price_total
                                exe_qty_service += recod.quantity
                            line.executed_cost = executed_cost
                            line.executed = exe_qty_service
                        
                elif ren.state == 'open':
                    to_amt = (ren.amount_total- ren.residual)/len(ren.invoice_line_ids)
                    for amts in ren.invoice_line_ids:
                        if line.name.id == amts.product_id.id:
                            executed_cost += to_amt
                        line.executed_cost = executed_cost
#                            
                  
            if line.qty > 0 and total > 0:
                line.percentage_qty = (total / line.qty)*100
            else:
                line.percentage_qty = 0.0
                
            if line.cantidad_total > 0 and executed_cost > 0:
                line.percentage_amt = (executed_cost / line.cantidad_total)*100
            else:
                line.percentage_amt = 0.0
            
            line.remaining_qty = line.qty-line.executed
            line.remaining_amt = line.cantidad_total-line.executed_cost
            
    @api.model
    def create(self, vals):

        rec=super(QuantityBudget, self).create(vals)
        total=self.search_count([('name', '=', rec.name.id), ('project_id', '=', rec.project_id.id)])
        if total>1:
            raise ValidationError(_('Product Category should not be repeat!'))
        return rec
    
    @api.onchange('name')
    def _onchange_category(self):
            if self.name:
                self.category_id=self.name.categ_id.id
                
     
    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """
            Override read_group to calculate the sum of the non-stored fields that depend on the user context
        """
        res = super(QuantityBudget, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        
        for line in res:
            accounts = self.env['qty.budget'].search(line['__domain'])
            accounts_len = self.env['qty.budget'].search_count(line['__domain'])
            if accounts:
                if 'executed' in fields:
                    line['executed'] = sum(accounts.mapped('executed'))
                    
                if 'executed_cost' in fields:
                    line['executed_cost'] = sum(accounts.mapped('executed_cost'))  
                    
                if 'percentage_qty' in fields:
                    line['percentage_qty'] = sum(accounts.mapped('percentage_qty'))/accounts_len 
                     
                if 'percentage_amt' in fields:
                    line['percentage_amt'] = sum(accounts.mapped('percentage_amt'))/accounts_len 
                    
                if 'remaining_amt' in fields:
                    line['remaining_amt'] = sum(accounts.mapped('remaining_amt'))    
                    
                if 'remaining_qty' in fields:
                    line['remaining_qty'] = sum(accounts.mapped('remaining_qty'))         
        return res
               
class AccountInvoice(models.Model):
    _inherit = "account.invoice"
    
#     project_acc_id = fields.Many2one("account.analytic.account",string="Analytic Account")
     
     
    @api.model
    def create(self, vals):
        if 'origin' in vals:
            purchase_ref_id  = self.env['purchase.order'].search([
                    ('name','=',vals['origin'])
                ])
            if purchase_ref_id:
                print("11")
                vals['purchase_id'] = purchase_ref_id.id
        
        res = super(AccountInvoice, self).create(vals)
        return res
        