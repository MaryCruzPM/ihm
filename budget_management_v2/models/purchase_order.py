# -*- coding: utf-8 -*-

from odoo import fields, models, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    product_list_id = fields.Many2one('product.list',string='Product List')
    
    @api.model
    def create(self, vals):
        # Override the original create function for the  model
        record = super(PurchaseOrder, self).create(vals)
        project_id = self.env['project.project'].search([('analytic_account_id','=',record.x_cuenta_analitica_id.id)])
        qty_rec_id = self.env['qty.budget'].search([('project_id','=',project_id.id)])
        if qty_rec_id:
            for line in record.order_line:
                rec_id = self.env['qty.budget'].search([('project_id','=',project_id.id),('name','=',line.product_id.id)])
                if not rec_id:
                    self.env['qty.budget'].create({
                        'name': line.product_id.id,
                        'category_id': line.product_id.categ_id.id,
                        'qty': line.product_qty,
                        'project_id' : project_id.id
        })
        else:
            for line in record.order_line:
                self.env['qty.budget'].create({
                    'name': line.product_id.id,
                    'category_id': line.product_id.categ_id.id,
                    'qty': line.product_qty,
                    'project_id' : project_id.id
        })
        return record
    
    @api.onchange('x_cuenta_analitica_id')
    def _onchange_location(self):
            location_id = self.env['project.project'].search([('analytic_account_id','=',self.x_cuenta_analitica_id.id)])
            if self.x_cuenta_analitica_id:
                self.picking_type_id = location_id.picking_id.id
                
                
      
                
                
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    analytic_acc_id = fields.Many2one('account.analytic.account',string='Analytic Account',compute="_compute_analytic_acc")  
    
    @api.one
    def _compute_analytic_acc(self):  
        if self.order_id.x_cuenta_analitica_id:
            self.analytic_acc_id =  self.order_id.x_cuenta_analitica_id.id             

