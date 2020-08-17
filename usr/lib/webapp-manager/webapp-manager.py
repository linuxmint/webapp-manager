#!/usr/bin/python3
import datetime
import gettext
import gi
import locale
import os
import setproctitle
import shutil
import subprocess
import tldextract
import urllib.parse
import warnings

# Suppress GTK deprecation warnings
warnings.filterwarnings("ignore")

gi.require_version("Gtk", "3.0")
gi.require_version('XApp', '1.0')
from gi.repository import Gtk, Gdk, Gio, XApp, GdkPixbuf

from common import _async, idle, WebAppManager, STATUS_OK

setproctitle.setproctitle("webapp-manager")

# i18n
APP = 'webapp-manager'
LOCALE_DIR = "/usr/share/locale"
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

COL_ICON, COL_NAME, COL_WEBAPP = range(3)
CATEGORY_ID, CATEGORY_NAME = range(2)
BROWSER_ID, BROWSER_NAME = range(2)

class MyApplication(Gtk.Application):
    # Main initialization routine
    def __init__(self, application_id, flags):
        Gtk.Application.__init__(self, application_id=application_id, flags=flags)
        self.connect("activate", self.activate)

    def activate(self, application):
        windows = self.get_windows()
        if (len(windows) > 0):
            window = windows[0]
            window.present()
            window.show()
        else:
            window = WebAppManagerWindow(self)
            self.add_window(window.window)
            window.window.show()

class WebAppManagerWindow():

    def __init__(self, application):

        self.application = application
        self.settings = Gio.Settings(schema_id="org.x.webapp-manager")
        self.manager = WebAppManager()
        self.selected_webapp = None
        self.icon_theme = Gtk.IconTheme.get_default()

        # Set the Glade file
        gladefile = "/usr/share/webapp-manager/webapp-manager.ui"
        self.builder = Gtk.Builder()
        self.builder.set_translation_domain(APP)
        self.builder.add_from_file(gladefile)
        self.window = self.builder.get_object("main_window")
        self.window.set_title(_("Web Apps"))
        self.window.set_icon_name("webapp-manager")
        self.stack = self.builder.get_object("stack")
        self.icon_chooser = XApp.IconChooserButton()
        self.builder.get_object("icon_button_box").pack_start(self.icon_chooser, 0, True, True)
        self.icon_chooser.set_icon("webapp-manager")
        self.icon_chooser.show()

        self.favicon_button = self.builder.get_object("favicon_button")

        # Widget signals
        self.builder.get_object("add_button").connect("clicked", self.on_add_button)
        #self.builder.get_object("edit_button").connect("clicked", self.on_edit_button)
        self.builder.get_object("remove_button").connect("clicked", self.on_remove_button)
        self.builder.get_object("ok_button").connect("clicked", self.on_ok_button)
        self.builder.get_object("cancel_button").connect("clicked", self.on_cancel_button)
        #self.builder.get_object("favicon_button").connect("clicked", self.on_favicon_button)
        self.builder.get_object("name_entry").connect("changed", self.on_name_entry)
        self.builder.get_object("url_entry").connect("changed", self.on_url_entry)

        # Menubar
        accel_group = Gtk.AccelGroup()
        self.window.add_accel_group(accel_group)
        menu = self.builder.get_object("main_menu")
        item = Gtk.ImageMenuItem()
        item.set_image(Gtk.Image.new_from_icon_name("help-about-symbolic", Gtk.IconSize.MENU))
        item.set_label(_("About"))
        item.connect("activate", self.open_about)
        key, mod = Gtk.accelerator_parse("<Control>H")
        item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        menu.append(item)
        item = Gtk.ImageMenuItem(label=_("Quit"))
        image = Gtk.Image.new_from_icon_name("application-exit-symbolic", Gtk.IconSize.MENU)
        item.set_image(image)
        item.connect('activate', self.on_menu_quit)
        key, mod = Gtk.accelerator_parse("<Control>Q")
        item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        key, mod = Gtk.accelerator_parse("<Control>W")
        item.add_accelerator("activate", accel_group, key, mod, Gtk.AccelFlags.VISIBLE)
        menu.append(item)
        menu.show_all()

        # Treeview
        self.treeview = self.builder.get_object("webapps_treeview")
        renderer = Gtk.CellRendererPixbuf()
        column = Gtk.TreeViewColumn("", renderer, pixbuf=COL_ICON)
        column.set_cell_data_func(renderer, self.data_func_surface)
        self.treeview.append_column(column)

        column = Gtk.TreeViewColumn("", Gtk.CellRendererText(), text=COL_NAME)
        column.set_sort_column_id(COL_NAME)
        column.set_resizable(True)
        self.treeview.append_column(column)
        self.treeview.show()
        self.model = Gtk.TreeStore(GdkPixbuf.Pixbuf, str, object) # icon, name, webapp
        self.model.set_sort_column_id(COL_NAME, Gtk.SortType.ASCENDING)
        self.treeview.set_model(self.model)
        self.treeview.get_selection().connect("changed", self.on_webapp_selected)

        # Combox box
        category_model = Gtk.ListStore(str,str) # CATEGORY_ID, CATEGORY_NAME
        category_model.append(["Network",_("Internet")])
        category_model.append(["Utility",_("Accessories")])
        category_model.append(["Game",_("Games")])
        category_model.append(["Graphics",_("Graphics")])
        category_model.append(["Office",_("Office")])
        category_model.append(["AudioVideo",_("Sound & Video")])
        category_model.append(["Development",_("Programming")])
        self.category_combo = self.builder.get_object("category_combo")
        renderer = Gtk.CellRendererText()
        self.category_combo.pack_start(renderer, True)
        self.category_combo.add_attribute(renderer, "text", CATEGORY_NAME)
        self.category_combo.set_model(category_model)
        self.category_combo.set_active(0) # Select 1st category

        browsers = []
        # path, codename, name
        browsers.append(["/usr/bin/firefox", "firefox", "Firefox"])
        browsers.append(["/usr/bin/brave-browser", "brave", "Brave"])
        browsers.append(["/usr/bin/google-chrome-stable", "google-chrome", "Chrome"])
        browsers.append(["/usr/bin/chromium-browser", "chromium-browser", "Chromium"])
        browsers.append(["/usr/bin/epiphany-browser", "epiphany", "Epiphany"])
        browsers.append(["/usr/bin/vivaldi-stable", "vivaldi", "Vivaldi"])
        browser_model = Gtk.ListStore(str, str) # BROWSER_ID, BROWSER_NAME
        num_browsers = 0
        for path, codename, name in browsers:
            if os.path.exists(path):
                browser_model.append([codename, name])
                num_browsers += 1
        self.browser_combo = self.builder.get_object("browser_combo")
        renderer = Gtk.CellRendererText()
        self.browser_combo.pack_start(renderer, True)
        self.browser_combo.add_attribute(renderer, "text", BROWSER_NAME)
        self.browser_combo.set_model(browser_model)
        self.browser_combo.set_active(0) # Select 1st browser
        if (num_browsers < 2):
            self.builder.get_object("browser_label").hide()
            self.browser_combo.hide()
        self.browser_combo.connect("changed", self.on_browser_changed)

        self.load_webapps()
        self.show_hide_isolated_widgets()

    def data_func_surface(self, column, cell, model, iter_, *args):
        pixbuf = model.get_value(iter_, COL_ICON)
        surface = Gdk.cairo_surface_create_from_pixbuf(pixbuf, self.window.get_scale_factor())
        cell.set_property("surface", surface)

    def open_about(self, widget):
        dlg = Gtk.AboutDialog()
        dlg.set_transient_for(self.window)
        dlg.set_title(_("About"))
        dlg.set_program_name(_("Web Apps"))
        dlg.set_comments(_("Run websites as if they were apps"))
        try:
            h = open('/usr/share/common-licenses/GPL', encoding="utf-8")
            s = h.readlines()
            gpl = ""
            for line in s:
                gpl += line
            h.close()
            dlg.set_license(gpl)
        except Exception as e:
            print (e)

        dlg.set_version("__DEB_VERSION__")
        dlg.set_icon_name("webapp-manager")
        dlg.set_logo_icon_name("webapp-manager")
        dlg.set_website("https://www.github.com/linuxmint/webapp-manager")
        def close(w, res):
            if res == Gtk.ResponseType.CANCEL or res == Gtk.ResponseType.DELETE_EVENT:
                w.destroy()
        dlg.connect("response", close)
        dlg.show()

    def on_menu_quit(self, widget):
        self.application.quit()

    def on_webapp_selected(self, selection):
        model, iter = selection.get_selected()
        if iter is not None:
            self.selected_webapp = model.get_value(iter, COL_WEBAPP)
            self.builder.get_object("edit_button").set_sensitive(True)
            self.builder.get_object("remove_button").set_sensitive(True)

    def on_remove_button(self, widget):
        if self.selected_webapp != None:
            self.manager.delete_webbapp(self.selected_webapp)
            self.load_webapps()

    def on_ok_button(self, widget):
        category = self.category_combo.get_model()[self.category_combo.get_active()][CATEGORY_ID]
        browser = self.browser_combo.get_model()[self.browser_combo.get_active()][BROWSER_ID]
        name = self.builder.get_object("name_entry").get_text()
        url = self.builder.get_object("url_entry").get_text()
        icon = self.icon_chooser.get_icon()
        isolate_profile = self.builder.get_object("isolated_switch").get_active()
        if (self.manager.create_webapp(name, url, icon, category, browser, isolate_profile) == STATUS_OK):
            self.stack.set_visible_child_name("main_page")
            self.load_webapps()
        else:
            self.builder.get_object("error_label").set_text(_("An error occurred"))

    def on_add_button(self, widget):
        self.stack.set_visible_child_name("add_page")

    def on_cancel_button(self, widget):
        self.stack.set_visible_child_name("main_page")

    def on_browser_changed(self, widget):
        self.show_hide_isolated_widgets()

    def show_hide_isolated_widgets(self):
        label = self.builder.get_object("isolated_label")
        switch = self.builder.get_object("isolated_switch")
        browser = self.browser_combo.get_model()[self.browser_combo.get_active()][BROWSER_ID]
        if (browser == "firefox"):
            label.hide()
            switch.hide()
        else:
            label.show()
            switch.show()

    def on_name_entry(self, widget):
        self.toggle_ok_sensitivity()

    def on_url_entry(self, widget):
        if widget.get_text() != "":
            self.favicon_button.set_sensitive(True)
        else:
            self.favicon_button.set_sensitive(False)
        self.toggle_ok_sensitivity()
        self.guess_icon()

    def toggle_ok_sensitivity(self):
        if self.builder.get_object("name_entry").get_text() == "" or self.builder.get_object("url_entry").get_text() == "":
            self.builder.get_object("ok_button").set_sensitive(False)
        else:
            self.builder.get_object("ok_button").set_sensitive(True)

    def guess_icon(self):
        url = self.builder.get_object("url_entry").get_text().lower()
        if "." in url:
            info = tldextract.extract(url)
            if info.domain == "google" and info.subdomain != None and info.subdomain != "":
                if info.subdomain == "mail":
                    icon = "web-%s-gmail" % info.domain
                else:
                    icon = "web-%s-%s" % (info.domain, info.subdomain)
                if self.icon_theme.has_icon(icon):
                    self.icon_chooser.set_icon(icon)
            elif info.domain != None and info.domain != "":
                icon = "web-%s" % info.domain
                if self.icon_theme.has_icon(icon):
                    self.icon_chooser.set_icon(icon)

    def load_webapps(self):
        # Clear treeview and selection
        self.model.clear()
        self.selected_webapp = None
        self.builder.get_object("edit_button").set_sensitive(False)
        self.builder.get_object("remove_button").set_sensitive(False)

        webapps = self.manager.get_webapps()
        for webapp in webapps:
            if webapp.is_valid:
                if "/" in webapp.icon and os.path.exists(webapp.icon):
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(webapp.icon, -1, 32 * self.window.get_scale_factor())
                else:
                    if self.icon_theme.has_icon(webapp.icon):
                        pixbuf = self.icon_theme.load_icon(webapp.icon, 32 * self.window.get_scale_factor(), 0)
                    else:
                        pixbuf = self.icon_theme.load_icon("webapp-manager", 32 * self.window.get_scale_factor(), 0)

                iter = self.model.insert_before(None, None)
                self.model.set_value(iter, COL_ICON, pixbuf)
                self.model.set_value(iter, COL_NAME, webapp.name)
                self.model.set_value(iter, COL_WEBAPP, webapp)

if __name__ == "__main__":
    application = MyApplication("org.x.webapp-manager", Gio.ApplicationFlags.FLAGS_NONE)
    application.run()
