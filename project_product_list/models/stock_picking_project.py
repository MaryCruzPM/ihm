# -*- coding: utf-8 -*-

from odoo import fields, models, api, _

class stockPickingProject(models.Model):
	_inherit = 'stock.picking'

	x_cuenta_analitica = fields.Many2one('account.analytic.account',string='Cuenta Analitica',
		readonly=True)
	campo_ejecucion_analitica = fields.Char(string='Campo de ejecución de la cuenta Analitica',compute='get_analytic_id')

	@api.model
	def get_analytic_id(self):
		for record in self:
			if record.x_cuenta_analitica != False:
				return record.get_product_stock()

	@api.multi
	def get_product_stock(self):
		for record in self.move_lines:
			print('PRODUCTOS-<<<>>>',str(record))
			for move in record.move_line_ids:
				move.sudo().write({'x_proyecto_id':record.x_proyecto.id})

class stockMoveProject(models.Model):
	_inherit = 'stock.move'

	x_proyecto = fields.Many2one('account.analytic.account',string='Cuenta Analitica',readonly=True)

class purchasOrderState(models.Model):
	_inherit = 'purchase.order'

	type = fields.Selection(selection=[('aprobada','Aprobada'),('no_aprobada','No Aprobada')],string='Estatus')
	campo_ejecucion = fields.Char(string='Campo de ejecución de método get_purchase_id',compute='get_purchase_id')

	@api.multi
	def get_purchase_id(self):
		if self.state == 'purchase':
			for record in self:
				for picking in record.picking_ids:
					picking.sudo().write({'x_cuenta_analitica':record.x_cuenta_analitica_id.id})
					for move in picking.move_lines:
						move.sudo().write({'x_proyecto':record.x_cuenta_analitica_id.id})


class stockQuantProject(models.Model):
	_inherit = 'stock.move.line'

	x_proyecto_id = fields.Many2one('account.analytic.account',string='Cuenta Analitica')

class orderLinePrioridad(models.Model):
	_inherit = 'purchase.order.line'

	x_prioridad = fields.Char(string='Prioridad',readonly=True)

class stockQuantT(models.Model):
	_inherit = 'stock.quant'

	@api.multi
	def open_wizard(self):
		ctx = {
			'product_id': self.product_id.id,
			'location_id':self.location_id.id,
			'quantity':self.quantity,
			'lot_id':self.lot_id.id
		}
		return {
			'name':'Transferir Productos',
			'type': 'ir.actions.act_window',
			'res_model': 'stock.quant.transfer',
			'view_type': 'form',
			'view_mode': 'form',
			'target': 'new',
			'context': ctx,
		}
