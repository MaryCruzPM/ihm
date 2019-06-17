# -*- coding: utf-8 -*-
from collections import defaultdict
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class productList(models.Model):
	_name = 'product.list'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	sequence = fields.Char('Referencia', required=True, index=True, copy=False, default='New')
	project_id = fields.Many2one('project.project',string='Proyecto',
		default=lambda self: self.env.context.get('default_project_id'),
		track_visibility='onchange',readonly=True)
	field_bool = fields.Boolean(default=False)
	product_list_ids = fields.One2many('product.list.line','product_list_id',string='Productos')
	pruchase_order_id = fields.Many2one('purchase.order')
	state = fields.Selection([
		('draft', 'En Elaboración'),
		('confirmed', 'En Validación'),
		('done', 'Lista Validada'),
		('purchase','RFQ Generada')
	], default='draft', readonly=True, track_visibility='onchange')
	name = fields.Char(string='Nombre',required=True)
	date = fields.Datetime(string='Fecha Requerida',default=fields.Datetime.now,required=True)
	type = fields.Selection(selection=[('alta','Alta'),('normal','Normal'),('baja','Baja')],
		track_visibility='onchange')
	is_locked = fields.Boolean(default=True)


#final
	@api.model
	def create(self, vals):
		if vals.get('sequence', 'New') == 'New':
			vals['sequence'] = self.env['ir.sequence'].next_by_code('product.list') or '/'
		return super(productList, self).create(vals)

	@api.multi
	def set_done(self):
		self.state = 'done'
		self.write({'is_locked':True})

	@api.multi
	def set_confirm(self):
		for record in self.product_list_ids:
			record.product.sudo().write({'x_qty_list':record.cantidad})
			record.product.sudo().write({'x_task':record.task_id.id})
			record.product.sudo().write({'x_fecha_requerida':record.fecha})
			record.product.sudo().write({'x_seleccion':record.type})
			print('FECHA ',record.product.x_fecha_requerida)
			print('SELECTION TYPE',record.type)
		#self.generar_orden_compra()
		self.state = 'confirmed'
		self.write({'is_locked':True})

	@api.multi
	def set_draft(self):
		self.state = 'draft'

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
		for record in self.product_list_ids:
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
#**********		


# # #************

			self.purchase_order(seller_mxn[0],seller_mxn[1],mxn[0])

		for seller_usd in seller_by_product_usd.items():
			print('FOR PROVEEDOR PREFERIDO MXN',seller_usd)
			#**********		

#************

			self.purchase_order(seller_usd[0],seller_usd[1],usd[0])

		for vendor_mxn in seller_products_mxn.items():
			print('FOR PROVEEDORES MXN',vendor_mxn)
			print('FOR PROVEEDORES MXN',mxn_seller)
	
#************
			self.purchase_order(vendor_mxn[0],vendor_mxn[1],mxn_seller[0])

		for vendor_usd in seller_products_usd.items():
			print('FOR PROVEEDORES USD',vendor_usd)
			print('FOR PROVEEDORES USD',usd_seller)
			#**********		
	
#************
			self.purchase_order(vendor_usd[0],vendor_usd[1],usd_seller[0])

	def purchase_order(self,seller,producto,currency_id):
		supplier = self.env['res.partner'].browse(seller)
		proyecto_id = self.project_id
		vals = {
			'date_order':fields.Datetime.now(),
			'x_cuenta_analitica_id':proyecto_id.analytic_account_id.id,
			'partner_id':supplier.id,
			'currency_id':currency_id
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
		r = self.pruchase_order_id
		r = res
		self.field_bool = True
		self.write({'is_locked':True})
		self.state = 'purchase'
		return r, res_line

class productListLine(models.Model):
	_name = 'product.list.line'

	product_list_id = fields.Many2one('product.list')
	product = fields.Many2one('product.product',string='Productos',required=True)
	project_id = fields.Many2one('project.project',
		default=lambda self: self.env.context.get('default_project_id'),store=True)
	task_id = fields.Many2one('project.task',store=True)
	cantidad = fields.Float(string='Cantidad')
	uom_lista = fields.Many2one('uom.uom', string="Unidad de medida", 
		related='product.uom_id',required=True,readonly=True)
	name = fields.Text(string='Notas')
	fecha = fields.Datetime(string='Fecha Requerida',default=fields.Datetime.now)
	type = fields.Selection(selection=[('alta','Alta'),('normal','Normal'),('baja','Baja')],string='Prioridad')
	state = fields.Selection([
		('draft', 'En Elaboración'),
		('confirmed', 'En Validación'),
		('done', 'Lista Validada'),
	], default='draft', readonly=True, related='product_list_id.state')

class productProject(models.Model):
	_inherit = 'project.project'

	product_list_count = fields.Integer(compute="get_product_list_count")

	def get_product_list_count(self):
		list_data = self.env['product.list'].read_group([('project_id','in',self.ids)],['project_id'],['project_id'])
		mapped_data = dict((data['project_id'][0], data['project_id_count']) for data in list_data)
		for project in self:
			project.product_list_count = mapped_data.get(project.id, 0)

class productTask(models.Model):
	_inherit = 'product.product'

	x_task = fields.Integer(string='Field Label')
	x_qty_list = fields.Integer(string='Field Label')
	x_seleccion = fields.Char(string='Filed Label')
	x_fecha_requerida = fields.Datetime(string='Field Label')