#!/usr/bin/python3

DOMAIN = "webapp-manager"
PATH = "/usr/share/locale"

import os
import gettext
from mintcommon import additionalfiles

os.environ['LANGUAGE'] = "en_US.UTF-8"
gettext.install(DOMAIN, PATH)

prefix = "[Desktop Entry]\n"

suffix = """Exec=webapp-manager
Icon=webapp-manager
Terminal=false
Type=Application
Encoding=UTF-8
Categories=Application;Network;
StartupNotify=false
NotShowIn=KDE;
"""

additionalfiles.generate(DOMAIN, PATH, "usr/share/applications/webapp-manager.desktop", prefix, _("Web Apps"), _("Run websites as if they were apps"), suffix)

prefix = "[Desktop Entry]\n"

suffix = """Exec=webapp-manager
Icon=webapp-manager
Terminal=false
Type=Application
Encoding=UTF-8
Categories=Application;Network;
X-KDE-StartupNotify=false
OnlyShowIn=KDE;
"""

additionalfiles.generate(DOMAIN, PATH, "usr/share/applications/kde4/webapp-manager.desktop", prefix, _("Web Apps"), _("Run websites as if they were apps"), suffix, genericName=_("Web Apps"))

prefix = """[Desktop Entry]
Type=Directory
"""

suffix = """Icon=applications-webapps
"""

additionalfiles.generate(DOMAIN, PATH, "usr/share/desktop-directories/webapps-webapps.directory", prefix, _("Web"), None, suffix)
