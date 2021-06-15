# Webapp Manager

Run websites as if they were apps.

## Contents
- [Dependencies](#dependencies)
- [How to Build and install](#how-to-build-and-install)
	- [Debian/Ubuntu based systems](#debian-or-ubuntu-based-systems)
	- [Other Unix-like systems](#other-unix-like-systems)
- [FAQ](#faq)
	- [How to go back without the navigation buttons?](#how-to-go-back-without-the-navigation-buttons)
	- [How to open links in my main browser?](#how-to-open-links-in-my-main-browser)
	- [How to use tabs in Firefox?](#how-to-use-tabs-in-firefox)
	- [How to add extensions in Firefox (AdBlock etc.)?](#how-to-add-extensions-in-firefox-(adblock-etc.))
	- [How to add extensions in Chromium based browsers (AdBlock etc.)?](#how-to-add-extensions-in-chromium-based-browsers-(adblock-etc.))

## Dependencies
```
gir1.2-xapp-1.0 (>= 1.4)
python3
python3-bs4
python3-configobj
python3-gi
python3-pil
python3-setproctitle
python3-tldextract
xapps-common
```

## How to Build and install
### Debian or Ubuntu based systems
1. Install dependencies:
	``` 
	sudo apt install gir1.2-xapp-1.0 python3 python3-bs4 python3-configobj \
	python3-gi python3-pil python3-setproctitle python3-tldextract xapps-common
	```

2. There are two methods, this app can be installed/used:
	1. **Option 1:** Manually copying necessary files to root (`/`). For that, follow the steps below:
		1. [**Optional**] To make translations/locales in languages other than **English**, run:
			```
			make
			```
			from the `/path/to/repo` in a terminal. It will create the translations/locales in `usr/share/locale`.

		2. Copy the contents of `etc` and `usr` to `/etc/` and `/usr/` respectively:
			```
			sudo cp -R usr etc /
			```
		3. Compile `schemas` using:
			```
			sudo glib-compile-schemas /usr/share/glib-2.0/schemas
			```
		4. Run `webapp-manager` from terminal or use the `webapp-manager.desktop`.

	2. **Option 2:** To build a *.deb package on your own, from the `/path/to/repo` run:
		```
		dpkg-buildpackage --no-sign
		```
		This will create a `webapp-manager_*.deb` package at `../path/to/repo`.

### Other Unix like systems:
From instructions for [Debian/Ubuntu based systems](#debian-or-ubuntu-based-systems), follow:
1. **Step _1_** replacing `apt install` with the *package manager* of target system.
2. **Option 1** from **Step _2_**

FAQ
===

How to go back without the navigation buttons?
----------------------------------------------

Right-click an empty area of the Web page to show the context menu. In most browsers this menu contains navigation buttons.

How to open links in my main browser?
-------------------------------------

For Firefox, all links are always opened within the WebApp, either directly or using a new tab.
To open a link in your main browser, right-click anywhere, select `Copy link location` and paste the link in your main browser. 

Chromium and Chrome WebApps open external links in the main browser.

How to use tabs in Firefox?
---------------------------

Press `Ctrl`+`Tab` to **cycle** between _opened tabs_.

Press `Ctrl`+`T` to **create** a _new tab_.

Press `Ctrl`+`W` to **close** the _current tab_.

Press `Ctrl` when clicking a link to **open** it in a _new tab_.

How to add extensions in Firefox (AdBlock etc.)?
------------------------------------------------

Press and release the `Alt` key to show the main menubar.

You can then reach the `Add-Ons` from the `Tool` menu.

How to add extensions in Chromium based browsers (AdBlock etc.)?
----------------------------------------------------------------

Press `ctrl+N` to open a __new window__.

Navigate to [Chrome Extensions Page](https://chrome.google.com/webstore/category/extensions).

Now add the extension.
