# -*- coding: utf-8 -*-
{
    'name': "ihm listado inmuebles",

    'summary': """
        Reporte de listado de inmuebles
        """,

    'description': """
        Listado de reporte de inmuebles
    """,

    'author': "Soluciones 4G",
    'website': "http://soluciones4g.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock', 'ihm_add_fields_productos',],

    # always loaded
    'data': [
        
        'views/listado_inmuebles.xml',
        
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
}