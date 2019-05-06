# -*- coding: utf-8 -*-
{
    'name': "Wizard para validación de facturas",

    'summary': """
    Wizard para validar factura
    """,

    'description': """
        wizard para validacion de facturas multiple
    """,

    'author': "Soluciones4G",
    'website': "http://www.soluciones4g.com",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'stock',        
    ],

    # always loaded
	'data': [
	'views/wizard_validar_factura.xml',
    ],
	'demo':[

	],
    'installable':True,
}
