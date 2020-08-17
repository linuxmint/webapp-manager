#!/usr/bin/python3
import gi
import os
import shutil
import threading
from gi.repository import GObject

# Used as a decorator to run things in the background
def _async(func):
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.daemon = True
        thread.start()
        return thread
    return wrapper

# Used as a decorator to run things in the main loop, from another thread
def idle(func):
    def wrapper(*args):
        GObject.idle_add(func, *args)
    return wrapper

# Constants
ICE_DIR = os.path.expanduser("~/.local/share/ice")
APPS_DIR = os.path.expanduser("~/.local/share/applications")
PROFILES_DIR = os.path.join(ICE_DIR, "profiles")
FIREFOX_PROFILES_DIR = os.path.join(ICE_DIR, "firefox")
EPIPHANY_PROFILES_DIR = os.path.join(ICE_DIR, "epiphany")
ICONS_DIR = os.path.join(ICE_DIR, "icons")
STATUS_OK, STATUS_ERROR_DUPLICATE, STATUS_ERROR_UNKNOWN_BROWSER = range(3)

# This is a data structure representing
# the app menu item (path, name, icon..etc.)
class WebAppLauncher():

    def __init__(self, path):
        self.path = path
        self.name = None
        self.icon = None
        self.profile = None
        self.is_webapp = False
        self.is_firefox = False
        self.is_isolated = False
        self.is_valid = False

        with open(path) as desktop_file:
            for line in desktop_file:
                line = line.strip()

                # Identify if the app is a webapp (we use ICE-SSB to keep compatibility with ICE)
                if "StartupWMClass=Chromium" in line or "StartupWMClass=ICE-SSB" in line:
                    self.is_webapp = True
                    continue

                if "Name=" in line:
                    self.name = line.replace("Name=", "")
                    continue

                if "Icon=" in line:
                    self.icon = line.replace("Icon=", "")
                    continue

                if "IceFirefox=" in line:
                    self.profile = line.replace('IceFirefox=', '')
                    self.is_firefox = True

                elif "X-ICE-SSB-Profile=" in line:
                    self.profile = line.replace('X-ICE-SSB-Profile=', '')
                    self.is_isolated = True

        if self.is_webapp and self.name != None and self.icon != None:
            self.is_valid = True

# This is the backend.
# It contains utility functions to load,
# save and delete webapps.
class WebAppManager():

    def __init__(self):
        for directory in [ICE_DIR, APPS_DIR, PROFILES_DIR, FIREFOX_PROFILES_DIR, ICONS_DIR, EPIPHANY_PROFILES_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def get_webapps(self):
        webapps = []
        for filename in os.listdir(APPS_DIR):
            path = os.path.join(APPS_DIR, filename)
            if not os.path.isdir(path):
                webapp = WebAppLauncher(path)
                if webapp.is_valid:
                    webapps.append(webapp)
        return (webapps)

    def delete_webbapp(self, webapp):
        if webapp.profile != None:
            shutil.rmtree(os.path.join(FIREFOX_PROFILES_DIR, webapp.profile), ignore_errors=True)
            shutil.rmtree(os.path.join(EPIPHANY_PROFILES_DIR, "/epiphany-%s" % webapp.profile), ignore_errors=True)
            shutil.rmtree(os.path.join(PROFILES_DIR, webapp.profile), ignore_errors=True)
        if os.path.exists(webapp.path):
            os.remove(webapp.path)

    def create_webapp(self, name, url, icon, category, browser, isolate_profile=True):
        codename = "".join(filter(str.isalpha, name))
        path = os.path.join(APPS_DIR, "%s.desktop" % codename)

        if os.path.exists(path):
            return (STATUS_ERROR_DUPLICATE)

        if not browser in ["google-chrome", "chromium-browser", "brave", "vivaldi", "firefox", "epiphany"]:
            return (STATUS_ERROR_UNKNOWN_BROWSER)

        with open(path, 'w') as desktop_file:
            desktop_file.write("[Desktop Entry]\n")
            desktop_file.write("Version=1.0\n")
            desktop_file.write("Name=%s\n" % name)
            desktop_file.write("Comment=%s (Web App)\n" % name)

            if browser == "firefox":
                firefox_profile_path = os.path.join(FIREFOX_PROFILES_DIR, codename)
                desktop_file.write("Exec=" + browser +
                                    " --class ICE-SSB-" + codename +
                                    " --profile " + firefox_profile_path +
                                    " --no-remote " + url + "\n")
                desktop_file.write("IceFirefox=%s\n" % codename)
                # Create a Firefox profile
                shutil.copytree('/usr/share/webapp-manager/firefox/profile', firefox_profile_path)
            elif browser == "epiphany":
                epiphany_profile_path = os.path.join(EPIPHANY_PROFILES_DIR, "epiphany-" + codename)
                desktop_file.write("Exec=" + browser +
                                    " --application-mode " +
                                    " --profile=\"" + epiphany_profile_path + "\"" +
                                    "" + url + "\n")
                desktop_file.write("IceEpiphany=%s\n" %codename)
            else:
                if isolate_profile:
                    profile_path = os.path.join(PROFILES_DIR, codename)
                    desktop_file.write("Exec=" + browser +
                                        " --app=" + url +
                                        " --class=ICE-SSB-" + codename +
                                        " --user-data-dir=" + profile_path + "\n")
                    desktop_file.write("X-ICE-SSB-Profile=%s\n" % codename)
                else:
                    desktop_file.write("Exec=" + browser +
                                        " --app=" + url +
                                        " --class=ICE-SSB-" + codename + "\n")

            desktop_file.write("Terminal=false\n")
            desktop_file.write("X-MultipleArgs=false\n")
            desktop_file.write("Type=Application\n")
            desktop_file.write("Icon=%s\n" % icon)
            desktop_file.write("Categories=GTK;%s;\n" % category)
            desktop_file.write("MimeType=text/html;text/xml;application/xhtml_xml;\n")
            desktop_file.write("StartupWMClass=ICE-SSB-%s\n" % codename)
            desktop_file.write("StartupNotify=true\n")

            if browser == "epiphany":
                # Move the desktop file and create a symlink
                new_path = os.path.join(profile_path, "epiphany-%s.desktop" % codename)
                os.makedirs(profile_path)
                os.replace(path, new_path)
                os.symlink(new_path, path)

        return (STATUS_OK)
