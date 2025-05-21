#!/usr/bin/env python3

from os import environ, path
from subprocess import call

if not environ.get('DESTDIR', ''):
    PREFIX = environ.get('MESON_INSTALL_PREFIX', '/usr')
    
    schemadir = path.join(PREFIX, 'share', 'glib-2.0', 'schemas')
    print('Compiling gsettings schemas...')
    call(['glib-compile-schemas', schemadir])
    
    themedir = path.join(PREFIX, 'share', 'icons', 'hicolor')
    print('Updating icon cache...')
    call(['gtk-update-icon-cache', '-qtf', themedir])
    
    mimedir = path.join(PREFIX, 'share', 'mime')
    print('Updating mime database...')
    call(['update-mime-database', mimedir])
