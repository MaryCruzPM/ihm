# -*- coding: utf-8 -*-
{
    'name': "Contrato categoria",

    'summary': """contrato para proveedor
    """,

    'description': """
        Modulo para hacer contrato con proveedores
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

	'data': [
    'views/categoria_contrato.xml',
    
#    'data/categorias.xml',

    ],
	'demo':[

	],
    'installable':True,
}
