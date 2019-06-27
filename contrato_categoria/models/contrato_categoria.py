# -*- coding: utf-8 -*-
from odoo import fields
from odoo import models,api

class ContratoCategoria(models.Model):
	_inherit = 'product.category'

	#se crean los tres campos a utilizar para el modulo de contrato
	#lo que se requiere es que desde categoria de productos, al crear 
	#una categoria poder crear desde ahi un contrato, seleccionara al crear categoria si es categoria o contrato
	#x_contrato es booleano para saber si esta sera un contrato o no
	#x_anticipo  o x_retencion 
	x_contrato = fields.Boolean(string='Contrato')

	x_anticipo = fields.Integer(string = 'Anticipo %')

	x_retencion = fields.Integer(string = 'Retencion %')

	




