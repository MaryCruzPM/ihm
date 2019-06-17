# -*- coding: utf-8 -*-

from odoo import fields, models, api


class stockQuantTransfer(models.TransientModel):
	_name = 'stock.quant.transfer'

	location_id = fields.Many2one('stock.location',string='Ubicación Origen',
		default=lambda self: self.env.context.get('location_id'),readonly=True)
	location_dest_id = fields.Many2one('stock.location',string='Ubicación Destino',required=True)
	product_id = fields.Many2one('product.product',string='Producto',default=lambda self: self.env.context.get('product_id'),readonly=True)
	qty = fields.Float(string='Cantidad',default=lambda self: self.env.context.get('quantity'))
	#lot_id = fields.Many2one('stock.production.lot', 'Lote/Nº de serie', default=lambda self: self.env.context.get('lot_id'),domain="[('product_id','=',product_id)]")

	def transfer_product_qty(self):
		order_lines = []
		for record in self:
			#print('names ',str(record.location_id.name),str(record.location_id.location_id.name))
			name = "%s %s" %(record.location_id.name, record.location_id.location_id.name)
			print('names ',str(name))
			picking_type = self.env['stock.picking.type'].search(['|','|',
				('name', '=', name),('name', '=', name+' entrega'),('name', '=', 'Stock')])
			project = self.env['project.project'].search([('name', '=', record.location_id.name)])
			print('picking type ',str(picking_type))
			for picking in picking_type:

				if picking.default_location_src_id.name == record.location_id.name and record.location_dest_id.usage == 'customer':
					if picking.code == 'outgoing':
						print('picking type outgoing ', str(picking.name))
						order_lines.append((0,0,{
							'state':'done',
							'name':record.product_id.name,
							'date_expected':fields.Datetime.now(),
							'product_id':record.product_id.id,
							'product_uom_qty':record.qty,
							'quantity_done':record.qty,
							'product_uom':record.product_id.uom_id.id,
							'x_proyecto':project.id
						}))
						self._create_main_picking(record.location_id.id,record.location_dest_id.id,
							picking.id,order_lines,project.id)
				if picking.default_location_src_id.name == record.location_id.name and record.location_dest_id.usage == 'internal':
					if picking.code == 'internal':
						print('picking type internal ', str(picking.name))
						order_lines.append((0,0,{
							'state':'done',
							'name':record.product_id.name,
							'date_expected':fields.Datetime.now(),
							'product_id':record.product_id.id,
							'product_uom_qty':record.qty,
							'quantity_done':record.qty,
							'product_uom':record.product_id.uom_id.id,
							'x_proyecto':project.id
						}))
						self._create_main_picking(record.location_id.id,record.location_dest_id.id,
							picking.id,order_lines,project.id)
			#order_lines.append((0,0,{
					#'state':'done',
					#'name':record.product_id.name,
					#'date_expected':fields.Datetime.now(),
					#'product_id':record.product_id.id,
					#'product_uom_qty':record.qty,
					#'quantity_done':record.qty,
					#'product_uom':record.product_id.uom_id.id,
					#'x_proyecto':project.id
				#}))
			#print('order lines',order_lines)
			#vals = {
				#'state':'done',
				#'location_id':record.location_id.id,
				#'location_dest_id':record.location_dest_id.id,
				#'picking_type_id': picking_type.id,
				#'move_lines': order_lines, 
				#'move_type': 'direct',
				#'priority': '1',
				#'x_cuenta_analitica':project.id,
			#}
			#print('CALS',vals)
			#res = self.env['stock.picking'].create(vals)
		#return res
	@api.multi
	def _create_main_picking(self, location_id,location_dest_id,picking_type,order_lines,project):
		self.ensure_one()

		vals = {
				'state':'done',
				'location_id':location_id,
				'location_dest_id':location_dest_id,
				'picking_type_id': picking_type,
				'move_lines': order_lines, 
				'move_type': 'direct',
				'priority': '1',
				'x_cuenta_analitica':project,
			}

		return self.env['stock.picking'].create(vals)