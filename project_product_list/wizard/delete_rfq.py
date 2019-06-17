# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError



class ClassName(models.TransientModel):
	_name = 'wizard.delete_rfq'

	def _default_rfq(self):
		return self.env['purchase.order'].browse(self._context.get('active_ids'))

	purchase_ids = fields.Many2many('purchase.order',string='RFQ',required=True,default=_default_rfq)

	@api.multi
	def delete_rfqs(self):
		for record in self.purchase_ids:
			if record.state == 'purchase':
				raise UserError(_('No se puede eliminar una RFQ que ya se ha convertido en Orden de Compra'))
			print(record)
			if record.type == 'no_aprobada' or record.type == ' ' or record.type == False:
				cancel = 'cancel'
				record.state = cancel
				record.unlink()
	@api.multi
	def rfqs_noaprobada(self):
		for record in self.purchase_ids:
			if record.type == ' ' or record.type == False:
				record.type = 'no_aprobada'