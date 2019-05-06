# -*- coding: utf-8 -*-

from odoo import _
from odoo import api
from odoo import exceptions
from odoo import fields
from odoo import models

class Wizard_Fac(models.TransientModel): 
    _name = 'wizard_val'
    
    def _default_descripcion(self):
        print("dentro de la funcion")
        return self.env['account.invoice'].browse(self._context.get('active_ids'))
        #active_ids son los campos seleccionados en la vista de árbol


    
    xcliente_ids = fields.Many2many('account.invoice', string='Facturas', default=_default_descripcion)

    def validar_add(self):
        for record in self.xcliente_ids:
            print("validad")
            record.action_invoice_open()
           