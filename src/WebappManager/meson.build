python_sources = files('common.py',	'main.py')

verconf= configuration_data()
verconf.set('version', meson.project_version())
version_file = configure_file(
  input: 'VERSION.in',
  output: 'VERSION',
  configuration: verconf,
  install: true,
  install_dir: pkgdatadir/'WebappManager',
)

install_data(
  python_sources,
  preserve_path: true,
  install_dir: pkgdatadir/'WebappManager',
)
