project('webapp-manager',
  version: run_command('head', '-1', 'debian/changelog', check: true).stdout().split(' ')[1].strip('(').strip(')'),
  license: ['GPL3'],
  meson_version: '>= 1.3.0',
  default_options: ['warning_level=3',
    'prefix=/usr',
  ]
)

application_id = meson.project_name()
i18n = import('i18n')
gnome = import('gnome')
pymod = import('python')
python = pymod.find_installation('python3')

prefix = get_option('prefix')
bindir = get_option('bindir')
datadir = get_option('datadir')

subdir('src')
subdir('data')
# subdir('po')

gnome.post_install(
     glib_compile_schemas: true,
    gtk_update_icon_cache: true,
  update_desktop_database: true,
)
