#!/usr/bin/python3

# Quickstart dialog — shown on first launch (zero or one  webapp(s) installed).
# Offers to create a default suite of Email, Notes, Reminders, and Contacts
# for the Google, Apple, or Microsoft ecosystem in one click.

import os
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

_ = lambda s: s  # i18n passthrough; real gettext is wired in the main module

# ---------------------------------------------------------------------------
# Ecosystem definitions
# Each entry lists the four web apps that will be created.
# ---------------------------------------------------------------------------
ECOSYSTEMS = [
    {
        "key":      "google",
        "label":    "Google",
        "icon":     "web-google",           # falls back gracefully if absent
        "color":    "#4285F4",
        "apps": [
            {"name": "Gmail",            "url": "https://mail.google.com",      "icon": "web-google-gmail", "desc": "Google email"},
            {"name": "Google Keep",      "url": "https://keep.google.com",      "icon": "web-google",       "desc": "Google notes"},
            {"name": "Google Tasks",     "url": "https://tasks.google.com",     "icon": "web-google",       "desc": "Google reminders"},
            {"name": "Google Contacts",  "url": "https://contacts.google.com",  "icon": "web-google",       "desc": "Google contacts"},
        ],
    },
    {
        "key":      "apple",
        "label":    "Apple",
        "icon":     "web-apple",            #changed from web-apple
        "color":    "#555555",
        "apps": [
            {"name": "iCloud Mail",       "url": "https://www.icloud.com/mail",       "icon": "web-apple", "desc": "iCloud email"},
            {"name": "iCloud Notes",      "url": "https://www.icloud.com/notes",      "icon": "web-apple", "desc": "iCloud notes"},
            {"name": "iCloud Reminders",  "url": "https://www.icloud.com/reminders",  "icon": "web-apple", "desc": "iCloud reminders"},
            {"name": "iCloud Contacts",   "url": "https://www.icloud.com/contacts",   "icon": "web-apple", "desc": "iCloud contacts"},
        ],
    },
    {
        "key":      "microsoft",
        "label":    "Microsoft",
        "icon":     "web-microsoft",
        "color":    "#00A4EF",
        "apps": [
            {"name": "Outlook Mail",    "url": "https://outlook.live.com/mail",       "icon": "web-microsoft", "desc": "Outlook email"},
            {"name": "OneNote",         "url": "https://www.onenote.com/notebooks",   "icon": "web-microsoft", "desc": "Microsoft notes"},
            {"name": "Microsoft To Do", "url": "https://to-do.office.com",            "icon": "web-microsoft", "desc": "Microsoft reminders"},
            {"name": "Outlook People",  "url": "https://outlook.live.com/people",     "icon": "web-microsoft", "desc": "Outlook contacts"},
        ],
    },
]

APP_LABELS = ["Email", "Notes", "Reminders", "Contacts"]


class QuickstartDialog:
    """
    Modal dialog shown when the user has no or one  web app(s) installed.
    Presents three ecosystem choices; clicking one creates all four apps
    automatically. Cancel dismisses without creating anything.
    """

    def __init__(self, parent_window, manager):
        self.manager = manager
        self.chosen_ecosystem = None

        # Resolve the first available browser once up-front
        self.browser = None
        for b in manager.get_supported_browsers():
            if os.path.exists(b.test_path):
                self.browser = b
                break

        # ------------------------------------------------------------------ #
        # Dialog shell
        # ------------------------------------------------------------------ #
        self.dialog = Gtk.Dialog()
        self.dialog.set_transient_for(parent_window)
        self.dialog.set_modal(True)
        self.dialog.set_resizable(False)
        self.dialog.set_title(_("Welcome to Web Apps"))
        self.dialog.set_default_size(560, -1)
        self.dialog.set_border_width(0)

        content = self.dialog.get_content_area()
        content.set_spacing(0)

        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        outer.set_border_width(28)
        content.pack_start(outer, True, True, 0)

        # ------------------------------------------------------------------ #
        # Header
        # ------------------------------------------------------------------ #
        header = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        header.set_halign(Gtk.Align.CENTER)

        app_icon = Gtk.Image.new_from_icon_name("webapp-manager", Gtk.IconSize.DIALOG)
        header.pack_start(app_icon, False, False, 0)

        title = Gtk.Label()
        title.set_markup("<span size='x-large' weight='bold'>%s</span>" % _("Welcome to Web Apps"))
        header.pack_start(title, False, False, 0)

        subtitle = Gtk.Label()
        subtitle.set_markup(
            "<span color='#777777'>%s</span>" %
            _("Pick an ecosystem to get Email, Notes, Reminders and Contacts\n"
              "installed as apps in one click.")
        )
        subtitle.set_justify(Gtk.Justification.CENTER)
        subtitle.set_line_wrap(True)
        header.pack_start(subtitle, False, False, 0)

        outer.pack_start(header, False, False, 0)

        # ------------------------------------------------------------------ #
        # Ecosystem cards
        # ------------------------------------------------------------------ #
        cards_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        cards_box.set_halign(Gtk.Align.CENTER)

        icon_theme = Gtk.IconTheme.get_default()

        for eco in ECOSYSTEMS:
            btn = self._make_card(eco, icon_theme)
            cards_box.pack_start(btn, False, False, 0)

        outer.pack_start(cards_box, False, False, 0)

        # ------------------------------------------------------------------ #
        # "Maybe later" cancel link
        # ------------------------------------------------------------------ #
        cancel_btn = Gtk.Button(label=_("Maybe later"))
        cancel_btn.set_halign(Gtk.Align.CENTER)
        cancel_btn.set_relief(Gtk.ReliefStyle.NONE)
        cancel_btn.connect("clicked", lambda w: self.dialog.destroy())
        outer.pack_start(cancel_btn, False, False, 0)

        self.dialog.show_all()

    # ---------------------------------------------------------------------- #
    # Helpers
    # ---------------------------------------------------------------------- #

    def _make_card(self, eco, icon_theme):
        """Return a styled button representing one ecosystem."""
        btn = Gtk.Button()
        btn.set_relief(Gtk.ReliefStyle.NONE)
        btn.set_sensitive(self.browser is not None)
        btn.set_tooltip_text(
            _("Create %s apps") % eco["label"] if self.browser
            else _("No supported browser detected.")
        )
        btn.connect("clicked", self._on_ecosystem_clicked, eco)

        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.set_border_width(14)

        # Ecosystem icon — graceful fallback
        icon_name = eco["icon"] if icon_theme.has_icon(eco["icon"]) else "web-browser"
        if not icon_theme.has_icon(icon_name):
            icon_name = "webapp-manager"
        eco_icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
        card.pack_start(eco_icon, False, False, 0)

        # Ecosystem name
        name_lbl = Gtk.Label()
        name_lbl.set_markup("<b>%s</b>" % eco["label"])
        card.pack_start(name_lbl, False, False, 0)

        # Four app labels
        for app_label in APP_LABELS:
            lbl = Gtk.Label()
            lbl.set_markup("<span size='small' color='#888888'>%s</span>" % app_label)
            card.pack_start(lbl, False, False, 0)

        btn.add(card)
        return btn

    def _on_ecosystem_clicked(self, _widget, eco):
        """Create all four apps for the chosen ecosystem then close."""
        if not self.browser:
            return

        icon_theme = Gtk.IconTheme.get_default()

        for app in eco["apps"]:
            # Resolve icon: prefer the specified one, fall back to webapp-manager
            icon = app["icon"]
            if not icon_theme.has_icon(icon):
                icon = "webapp-manager"

            self.manager.create_webapp(
                name=app["name"],
                desc=app["desc"],
                url=app["url"],
                icon=icon,
                category="Network",
                browser=self.browser,
                custom_parameters="",
                isolate_profile=True,
                navbar=False,
                privatewindow=False,
            )

        self.chosen_ecosystem = eco["key"]
        self.dialog.destroy()

    # ---------------------------------------------------------------------- #
    # Public API
    # ---------------------------------------------------------------------- #

    def run(self):
        """
        Show the dialog and block until it closes.
        Returns the chosen ecosystem key ("google" / "apple" / "microsoft"),
        or None if the user cancelled.
        """
        self.dialog.run()
        return self.chosen_ecosystem
