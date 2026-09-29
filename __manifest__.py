# -*- coding: utf-8 -*-
{
    'name': 'Delete Anything',
    'version': '19.0.1.0.0',
    'category': 'Technical/Administration',
    'summary': 'Instantly force-delete records or truncate tables with Ctrl+D shortcut and Systray button',
    'description': """
Delete Anything Tool
====================
Specialized administration and developer tool to force-delete records
or truncate database tables with foreign key cascade handling.

Features:
- Global shortcut: Ctrl + D
- Systray icon beside Debug mode menu
- Dual mode: Safe Mode (ORM unlink) and Force Mode (Raw SQL CASCADE)
- System table protection
- Cache invalidation
    """,
    'author': 'Johnny',
    'license': 'LGPL-3',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'views/delete_anything_wizard_views.xml',
        'views/delete_anything_menus.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'delete_anything/static/src/**/*',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
}
