user_pref("browser.cache.disk.enable", false);
user_pref("browser.cache.disk.capacity", 0);
user_pref("browser.cache.disk.filesystem_reported", 1);
user_pref("browser.cache.disk.smart_size.enabled", false);
user_pref("browser.cache.disk.smart_size.first_run", false);
user_pref("browser.cache.disk.smart_size.use_old_max", false);
user_pref("browser.ctrlTab.previews", true);
user_pref("browser.tabs.warnOnClose", false);
user_pref("plugin.state.flash", 2);
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);

// Always show titlebar on top of window
user_pref("browser.tabs.drawInTitlebar", false);
user_pref("browser.tabs.inTitlebar", 0);

// Enable strict mode for cookie isolation and enhanced privacy
user_pref("browser.contentblocking.category", "strict");

// Don't clear cookies in LibreWolf (and other Firefox forks)
user_pref("privacy.clearOnShutdown.offlineApps", false);
user_pref("privacy.sanitize.sanitizeOnShutdown", false);
user_pref("privacy.sanitize.timeSpan", 1);

// Don't show translations popups
user_pref("browser.translations.automaticallyPopup", false);

// Open links in new window
user_pref("browser.link.open_newwindow", 2);
