pkgdatadir = join_paths(prefix, 'lib', application_id)
message(f'pkgdata dir: @pkgdatadir@')

conf = configuration_data()
conf.set('PYTHON', python.full_path())
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'webapp-manager.in',
  output: 'webapp-manager',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

subdir('WebappManager')
