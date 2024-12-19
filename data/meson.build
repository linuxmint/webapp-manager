app_icon_dir = join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps')
category_icon_dir = join_paths(datadir, 'icons', 'hicolor', 'scalable', 'categories')
schema_dir = join_paths(datadir, 'glib-2.0', 'schemas')
# message(f'Icon dir: @app_icon_dir@')
# message(f'Schema dir: @schema_dir@')

# install icons
install_emptydir(app_icon_dir)
install_data(
  join_paths(meson.current_source_dir(), 'icons', f'@application_id@.svg'),
  install_dir: app_icon_dir,
)

install_data(
  join_paths(meson.current_source_dir(), 'icons/categories/applications-webapps.svg'),
  install_dir: category_icon_dir,
)


# Install desktop file
# desktop_file = i18n.merge_file(
#         input: 'webapp-manager.desktop.in',
#        output: 'webapp-manager.desktop',
#          type: 'desktop',
#        po_dir: '../po',
#       install: true,
#   install_dir: desktop_dir
# )

# Install schema file
schema_file = i18n.merge_file(
        input: 'org.x.webapp-manager.gschema.xml.in',
       output: 'org.x.webapp-manager.gschema.xml',
         type: 'xml',
       po_dir: '../po',
      install: true,
  install_dir: schema_dir
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file',
       compile_schemas,
       args: ['--strict', '--dry-run', meson.current_source_dir()])
endif
