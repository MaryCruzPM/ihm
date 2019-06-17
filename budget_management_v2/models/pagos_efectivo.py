# -*- coding: utf-8 -*-

from odoo import api
from odoo import fields
from odoo import models


class PagosEfectivo(models.Model):
    _name = 'pagos.efectivo'
    
    _description = 'Pagos en Efectivo'
    
    name = fields.Char(
                       string="Concepto"
                       )
    cantidad = fields.Float(
                            string="Cantidad",
                            default=0.0
                            )
    importe = fields.Float(
                            string="Importe",
                            
                           )
    proyecto_id = fields.Many2one(
                                'project.project',
                                   string="Proyecto"
                                   )

    