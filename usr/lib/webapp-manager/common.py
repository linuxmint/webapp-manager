#!/usr/bin/python3

#   1. Standard library imports.
import configparser
import gettext
from io import BytesIO
import json
import locale
import os
from random import choice
import shutil
import string
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import threading
import traceback

#   2. Related third party imports.
from gi.repository import GObject
from PIL import Image
import requests
# Note: BeautifulSoup is an optional import supporting another way of getting a website's favicons.


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

# i18n
APP = 'webapp-manager'
LOCALE_DIR = "/usr/share/locale"
locale.bindtextdomain(APP, LOCALE_DIR)
gettext.bindtextdomain(APP, LOCALE_DIR)
gettext.textdomain(APP)
_ = gettext.gettext

# Constants
ICE_DIR = os.path.expanduser("~/.local/share/ice")
APPS_DIR = os.path.expanduser("~/.local/share/applications")
PROFILES_DIR = os.path.join(ICE_DIR, "profiles")
FIREFOX_PROFILES_DIR = os.path.join(ICE_DIR, "firefox")
FIREFOX_FLATPAK_PROFILES_DIR = os.path.expanduser("~/.var/app/org.mozilla.firefox/data/ice/firefox")
LIBREWOLF_FLATPAK_PROFILES_DIR = os.path.expanduser("~/.var/app/io.gitlab.librewolf-community/data/ice/librewolf")
EPIPHANY_PROFILES_DIR = os.path.join(ICE_DIR, "epiphany")
FALKON_PROFILES_DIR = os.path.join(ICE_DIR, "falkon")
ICONS_DIR = os.path.join(ICE_DIR, "icons")
BROWSER_TYPE_FIREFOX, BROWSER_TYPE_FIREFOX_FLATPAK, BROWSER_TYPE_LIBREWOLF_FLATPAK, BROWSER_TYPE_CHROMIUM, BROWSER_TYPE_EPIPHANY, BROWSER_TYPE_FALKON = range(6)

class Browser():

    def __init__(self, browser_type, name, exec_path, test_path):
        self.browser_type = browser_type
        self.name = name
        self.exec_path = exec_path
        self.test_path = test_path

# This is a data structure representing
# the app menu item (path, name, icon..etc.)
class WebAppLauncher():

    def __init__(self, path, codename):
        self.path = path
        self.codename = codename
        self.web_browser = None
        self.name = None
        self.icon = None
        self.is_valid = False
        self.exec = None
        self.category = None
        self.url = ""
        self.custom_parameters = ""

        is_webapp = False
        with open(path) as desktop_file:
            for line in desktop_file:
                line = line.strip()

                # Identify if the app is a webapp
                if "StartupWMClass=WebApp" in line or "StartupWMClass=Chromium" in line or "StartupWMClass=ICE-SSB" in line:
                    is_webapp = True
                    continue

                if "Name=" in line:
                    self.name = line.replace("Name=", "")
                    continue

                if "Icon=" in line:
                    self.icon = line.replace("Icon=", "")
                    continue

                if "Exec=" in line:
                    self.exec = line.replace("Exec=", "")
                    continue

                if "Categories=" in line:
                    self.category = line.replace("Categories=", "").replace("GTK;", "").replace(";", "")
                    continue

                if "X-WebApp-Browser=" in line:
                    self.web_browser = line.replace("X-WebApp-Browser=", "")
                    continue

                if "X-WebApp-URL=" in line:
                    self.url = line.replace("X-WebApp-URL=", "")
                    continue

                if "X-WebApp-CustomParameters" in line:
                    self.custom_parameters = line.replace("X-WebApp-CustomParameters=", "")
                    continue

        if is_webapp and self.name is not None and self.icon is not None:
            self.is_valid = True

# This is the backend.
# It contains utility functions to load,
# save and delete webapps.
class WebAppManager():

    def __init__(self):
        for directory in [ICE_DIR, APPS_DIR, PROFILES_DIR, FIREFOX_PROFILES_DIR, FIREFOX_FLATPAK_PROFILES_DIR, ICONS_DIR, EPIPHANY_PROFILES_DIR, FALKON_PROFILES_DIR]:
            if not os.path.exists(directory):
                os.makedirs(directory)

    def get_webapps(self):
        webapps = []
        for filename in os.listdir(APPS_DIR):
            if filename.startswith("webapp-") and filename.endswith(".desktop"):
                path = os.path.join(APPS_DIR, filename)
                codename = filename.replace("webapp-", "").replace(".desktop", "")
                if not os.path.isdir(path):
                    try:
                        webapp = WebAppLauncher(path, codename)
                        if webapp.is_valid:
                            webapps.append(webapp)
                    except Exception:
                        print("Could not create webapp for path", path)
                        traceback.print_exc()

        return (webapps)

    def get_supported_browsers(self):
        browsers = []
        # type, name, exec, test
        browsers.append(Browser(BROWSER_TYPE_FIREFOX, "Firefox", "firefox", "/usr/bin/firefox"))
        browsers.append(Browser(BROWSER_TYPE_FIREFOX, "Firefox Developer Edition", "firefox-developer-edition", "/usr/bin/firefox-developer-edition"))
        browsers.append(Browser(BROWSER_TYPE_FIREFOX, "Firefox Extended Support Release", "firefox-esr", "/usr/bin/firefox-esr"))
        browsers.append(Browser(BROWSER_TYPE_FIREFOX_FLATPAK, "Firefox (Flatpak)", "/var/lib/flatpak/exports/bin/org.mozilla.firefox", "/var/lib/flatpak/exports/bin/org.mozilla.firefox"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Brave", "brave", "/usr/bin/brave"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Brave Browser", "brave-browser", "/usr/bin/brave-browser"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Chrome", "google-chrome-stable", "/usr/bin/google-chrome-stable"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Chrome (Beta)", "google-chrome-beta", "/usr/bin/google-chrome-beta"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Chrome (Flatpak)", "/var/lib/flatpak/exports/bin/com.google.Chrome", "/var/lib/flatpak/exports/bin/com.google.Chrome"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Chromium", "chromium", "/usr/bin/chromium"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Chromium (chromium-browser)", "chromium-browser", "/usr/bin/chromium-browser"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Chromium (Snap)", "chromium", "/snap/bin/chromium"))
        browsers.append(Browser(BROWSER_TYPE_EPIPHANY, "Epiphany", "epiphany", "/usr/bin/epiphany"))
        browsers.append(Browser(BROWSER_TYPE_FIREFOX,  "LibreWolf", "librewolf", "/usr/bin/librewolf"))
        browsers.append(Browser(BROWSER_TYPE_LIBREWOLF_FLATPAK,  "LibreWolf (Flatpak)", "/var/lib/flatpak/exports/bin/io.gitlab.librewolf-community", "/var/lib/flatpak/exports/bin/io.gitlab.librewolf-community"))
        browsers.append(Browser(BROWSER_TYPE_FIREFOX,  "Waterfox", "waterfox", "/usr/bin/waterfox"))
        browsers.append(Browser(BROWSER_TYPE_FIREFOX,  "Waterfox Current", "waterfox-current", "/usr/bin/waterfox-current"))
        browsers.append(Browser(BROWSER_TYPE_FIREFOX,  "Waterfox Classic", "waterfox-classic", "/usr/bin/waterfox-classic"))
        browsers.append(Browser(BROWSER_TYPE_FIREFOX,  "Waterfox 3rd Generation", "waterfox-g3", "/usr/bin/waterfox-g3"))
        browsers.append(Browser(BROWSER_TYPE_FIREFOX,  "Waterfox 4th Generation", "waterfox-g4", "/usr/bin/waterfox-g4"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Vivaldi", "vivaldi-stable", "/usr/bin/vivaldi-stable"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Vivaldi Snapshot", "vivaldi-snapshot", "/usr/bin/vivaldi-snapshot"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Microsoft Edge", "microsoft-edge-stable", "/usr/bin/microsoft-edge-stable"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Microsoft Edge Beta", "microsoft-edge-beta", "/usr/bin/microsoft-edge-beta"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Microsoft Edge Dev", "microsoft-edge-dev", "/usr/bin/microsoft-edge-dev"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "FlashPeak Slimjet", "flashpeak-slimjet", "/usr/bin/flashpeak-slimjet"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Ungoogled Chromium (Flatpak)", "/var/lib/flatpak/exports/bin/com.github.Eloston.UngoogledChromium", "/var/lib/flatpak/exports/bin/com.github.Eloston.UngoogledChromium"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Chromium (Flatpak)", "/var/lib/flatpak/exports/bin/org.chromium.Chromium", "/var/lib/flatpak/exports/bin/org.chromium.Chromium"))
        browsers.append(Browser(BROWSER_TYPE_FALKON, "Falkon", "falkon", "/usr/bin/falkon"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Edge (Flatpak)", "/var/lib/flatpak/exports/bin/com.microsoft.Edge", "/var/lib/flatpak/exports/bin/com.microsoft.Edge"))
        browsers.append(Browser(BROWSER_TYPE_CHROMIUM, "Brave (Flatpak)", "/var/lib/flatpak/exports/bin/com.brave.Browser", "/var/lib/flatpak/exports/bin/com.brave.Browser"))
        return browsers

    def delete_webbapp(self, webapp):
        shutil.rmtree(os.path.join(FIREFOX_PROFILES_DIR, webapp.codename), ignore_errors=True)
        shutil.rmtree(os.path.join(PROFILES_DIR, webapp.codename), ignore_errors=True)
        # first remove symlinks then others
        if os.path.exists(webapp.path):
            os.remove(webapp.path)
        epiphany_orig_prof_dir=os.path.join(os.path.expanduser("~/.local/share"), "org.gnome.Epiphany.WebApp-" + webapp.codename)
        if os.path.exists(epiphany_orig_prof_dir):
            os.remove(epiphany_orig_prof_dir)
        shutil.rmtree(os.path.join(EPIPHANY_PROFILES_DIR, "org.gnome.Epiphany.WebApp-%s" % webapp.codename), ignore_errors=True)

    def create_webapp(self, name, url, icon, category, browser, custom_parameters, isolate_profile=True, navbar=False, privatewindow=False):
        # Generate a 4 digit random code (to prevent name collisions, so we can define multiple launchers with the same name)
        random_code =  ''.join(choice(string.digits) for _ in range(4))
        codename = "".join(filter(str.isalpha, name)) + random_code
        path = os.path.join(APPS_DIR, "webapp-%s.desktop" % codename)

        with open(path, 'w') as desktop_file:
            desktop_file.write("[Desktop Entry]\n")
            desktop_file.write("Version=1.0\n")
            desktop_file.write("Name=%s\n" % name)
            desktop_file.write("Comment=%s\n" % _("Web App"))

            exec_string = self.get_exec_string(browser, codename, custom_parameters, icon, isolate_profile, navbar,
                                               privatewindow, url)

            desktop_file.write(exec_string + "\n")

            desktop_file.write("Terminal=false\n")
            desktop_file.write("X-MultipleArgs=false\n")
            desktop_file.write("Type=Application\n")
            desktop_file.write("Icon=%s\n" % icon)
            desktop_file.write("Categories=GTK;%s;\n" % category)
            desktop_file.write("MimeType=text/html;text/xml;application/xhtml_xml;\n")
            desktop_file.write("StartupWMClass=WebApp-%s\n" % codename)
            desktop_file.write("StartupNotify=true\n")
            desktop_file.write("X-WebApp-Browser=%s\n" % browser.name)
            desktop_file.write("X-WebApp-URL=%s\n" % url)
            desktop_file.write("X-WebApp-CustomParameters=%s\n" % custom_parameters)
            if isolate_profile:
                desktop_file.write("X-WebApp-Isolated=true\n")
            else:
                desktop_file.write("X-WebApp-Isolated=false\n")

            if browser.browser_type == BROWSER_TYPE_EPIPHANY:
                # Move the desktop file and create a symlink
                epiphany_profile_path = os.path.join(EPIPHANY_PROFILES_DIR, "org.gnome.Epiphany.WebApp-" + codename)
                new_path = os.path.join(epiphany_profile_path, "org.gnome.Epiphany.WebApp-%s.desktop" % codename)
                os.makedirs(epiphany_profile_path)
                os.replace(path, new_path)
                os.symlink(new_path, path)
                # copy the icon to profile directory
                new_icon=os.path.join(epiphany_profile_path, "app-icon.png")
                shutil.copy(icon, new_icon)
                # required for app mode. create an empty file .app
                app_mode_file=os.path.join(epiphany_profile_path, ".app")
                with open(app_mode_file, 'w') as fp:
                    pass

    def get_exec_string(self, browser, codename, custom_parameters, icon, isolate_profile, navbar, privatewindow, url):
        if browser.browser_type in [BROWSER_TYPE_FIREFOX, BROWSER_TYPE_FIREFOX_FLATPAK]:
            # Firefox based
            firefox_profiles_dir = FIREFOX_PROFILES_DIR if browser.browser_type == BROWSER_TYPE_FIREFOX else FIREFOX_FLATPAK_PROFILES_DIR
            firefox_profile_path = os.path.join(firefox_profiles_dir, codename)
            exec_string = ("Exec=sh -c 'XAPP_FORCE_GTKWINDOW_ICON=\"" + icon + "\" " + browser.exec_path +
                           " --class WebApp-" + codename +
                           " --profile " + firefox_profile_path +
                           " --no-remote ")
            if privatewindow:
                exec_string += "--private-window "
            if custom_parameters:
                exec_string += " {}".format(custom_parameters)
            exec_string += "\"" + url + "\"" + "'\n"
            # Create a Firefox profile
            shutil.copytree('/usr/share/webapp-manager/firefox/profile', firefox_profile_path)
            if navbar:
                shutil.copy('/usr/share/webapp-manager/firefox/userChrome-with-navbar.css',
                            os.path.join(firefox_profile_path, "chrome", "userChrome.css"))
        elif browser.browser_type == BROWSER_TYPE_LIBREWOLF_FLATPAK:
            # LibreWolf flatpak
            firefox_profiles_dir = LIBREWOLF_FLATPAK_PROFILES_DIR
            firefox_profile_path = os.path.join(firefox_profiles_dir, codename)
            exec_string = ("Exec=sh -c 'XAPP_FORCE_GTKWINDOW_ICON=\"" + icon + "\" " + browser.exec_path +
                           " --class WebApp-" + codename +
                           " --profile " + firefox_profile_path +
                           " --no-remote ")
            if privatewindow:
                exec_string += "--private-window "
            exec_string += "\"" + url + "\"" + "'\n"
            # Create a Firefox profile
            shutil.copytree('/usr/share/webapp-manager/firefox/profile', firefox_profile_path)
            if navbar:
                shutil.copy('/usr/share/webapp-manager/firefox/userChrome-with-navbar.css',
                            os.path.join(firefox_profile_path, "chrome", "userChrome.css"))
        elif browser.browser_type == BROWSER_TYPE_EPIPHANY:
            # Epiphany based
            epiphany_profile_path = os.path.join(EPIPHANY_PROFILES_DIR, "org.gnome.Epiphany.WebApp-" + codename)
            # Create symlink of profile dir at ~/.local/share
            epiphany_orig_prof_dir = os.path.join(os.path.expanduser("~/.local/share"),
                                                  "org.gnome.Epiphany.WebApp-" + codename)
            os.symlink(epiphany_profile_path, epiphany_orig_prof_dir)
            exec_string = "Exec=" + browser.exec_path
            exec_string += " --application-mode "
            exec_string += " --profile=\"" + epiphany_orig_prof_dir + "\""
            exec_string += " " + "\"" + url + "\"" + "\n"
            if custom_parameters:
                exec_string += " {}".format(custom_parameters)
        else:
            # Chromium based
            if isolate_profile:
                profile_path = os.path.join(PROFILES_DIR, codename)
                exec_string = ("Exec=" + browser.exec_path +
                               " --app=" + "\"" + url + "\"" +
                               " --class=WebApp-" + codename +
                               " --user-data-dir=" + profile_path)
            else:
                exec_string = ("Exec=" + browser.exec_path +
                               " --app=" + "\"" + url + "\"" +
                               " --class=WebApp-" + codename)

            if privatewindow:
                if browser.name == "Microsoft Edge":
                    exec_string += " --inprivate"
                elif browser.name == "Microsoft Edge Beta":
                    exec_string += " --inprivate"
                elif browser.name == "Microsoft Edge Dev":
                    exec_string += " --inprivate"
                else:
                    exec_string += " --incognito"

            if custom_parameters:
                exec_string += " {}".format(custom_parameters)

            exec_string += "\n"
        return exec_string

    def edit_webapp(self, path, name, browser, url, icon, category, custom_parameters):
        config = configparser.RawConfigParser()
        config.optionxform = str
        config.read(path)
        config.set("Desktop Entry", "Name", name)
        config.set("Desktop Entry", "Icon", icon)
        config.set("Desktop Entry", "Comment", _("Web App"))
        config.set("Desktop Entry", "Categories", "GTK;%s;" % category)

        try:
            # This will raise an exception on legacy apps which
            # have no X-WebApp-URL and X-WebApp-Browser
            old_url = config.get("Desktop Entry", "X-WebApp-URL")
            exec_line = config.get("Desktop Entry", "Exec")
            exec_line = exec_line.replace(old_url, url)
            old_custom_parameters = config.get("Desktop Entry", "X-WebApp-CustomParameters")
            exec_line = exec_line.replace(old_custom_parameters, custom_parameters)
            config.set("Desktop Entry", "Exec", exec_line)
            config.set("Desktop Entry", "X-WebApp-Browser", browser.name)
            config.set("Desktop Entry", "X-WebApp-URL", url)
            config.set("Desktop Entry", "X-WebApp-CustomParameters", custom_parameters)
        except:
            print("This WebApp was created with an old version of WebApp Manager. Its URL cannot be edited.")

        with open(path, 'w') as configfile:
            config.write(configfile, space_around_delimiters=False)


def normalize_url(url):
    (scheme, netloc, path, _, _, _) = urllib.parse.urlparse(url, "http")
    if not netloc and path:
        return urllib.parse.urlunparse((scheme, path, "", "", "", ""))
    return urllib.parse.urlunparse((scheme, netloc, path, "", "", ""))

def download_image(root_url, link):
    image = None
    if ("://") not in link:
        if link.startswith("/"):
            link = root_url + link
        else:
            link = root_url + "/" + link
    try:
        response = requests.get(link, timeout=3)
        image = Image.open(BytesIO(response.content))
        if image.height > 256:
            image = image.resize((256, 256), Image.BICUBIC)
    except Exception as e:
        print(e)
        print(link)
        image = None
    return image

def _find_link_favicon(soup, iconformat):
    items = soup.find_all("link", {"rel": iconformat})
    for item in items:
        link = item.get("href")
        if link:
            yield link

def _find_meta_content(soup, iconformat):
    item = soup.find("meta", {"name": iconformat})
    if not item:
        return
    link = item.get("content")
    if link:
        yield link

def _find_property(soup, iconformat):
    items = soup.find_all("meta", {"property": iconformat})
    for item in items:
        link = item.get("content")
        if link:
            yield link

def _find_url(_soup, iconformat):
    yield iconformat


def download_favicon(url):
    images = []
    url = normalize_url(url)
    (scheme, netloc, path, _, _, _) = urllib.parse.urlparse(url)
    root_url = "%s://%s" % (scheme, netloc)

    # try favicon grabber first
    try:
        response = requests.get("https://favicongrabber.com/api/grab/%s?pretty=true" % netloc, timeout=3)
        if response.status_code == 200:
            source = response.content.decode("UTF-8")
            array = json.loads(source)
            for icon in array['icons']:
                image = download_image(root_url, icon['src'])
                if image is not None:
                    t = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                    images.append(["Favicon Grabber", image, t.name])
                    image.save(t.name)
            images = sorted(images, key = lambda x: (x[1].height), reverse=True)
            if images:
                return images
    except Exception as e:
        print(e)

    # Fallback: Check HTML and /favicon.ico
    try:
        response = requests.get(url, timeout=3)
        if response.ok:
            import bs4
            soup = bs4.BeautifulSoup(response.content, "html.parser")

            iconformats = [
                ("apple-touch-icon", _find_link_favicon),
                ("shortcut icon", _find_link_favicon),
                ("icon", _find_link_favicon),
                ("msapplication-TileImage", _find_meta_content),
                ("msapplication-square310x310logo", _find_meta_content),
                ("msapplication-square150x150logo", _find_meta_content),
                ("msapplication-square70x70logo", _find_meta_content),
                ("og:image", _find_property),
                ("favicon.ico", _find_url),
            ]

            # icons defined in the HTML
            for (iconformat, getter) in iconformats:
                for link in getter(soup, iconformat):
                    image = download_image(root_url, link)
                    if image is not None:
                        t = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                        images.append([iconformat, image, t.name])
                        image.save(t.name)

    except Exception as e:
        print(e)

    images = sorted(images, key = lambda x: (x[1].height), reverse=True)
    return images

if __name__ == "__main__":
    download_favicon(sys.argv[1])
