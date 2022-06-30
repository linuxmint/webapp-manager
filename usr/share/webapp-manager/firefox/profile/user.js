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
user_pref("browser.tabs.drawInTitlebar", false);
user_pref("browser.tabs.inTitlebar", 0);
user_pref("browser.contentblocking.category", "strict");
user_pref("network.cookie.lifetimePolicy", 0);

// Disables "Recommend extensions as you browse" and "Recommend features as you browse"
// https://support.mozilla.org/en-US/kb/recommendations-firefox
user_pref(
  "browser.newtabpage.activity-stream.asrouter.userprefs.cfr.addons",
  false
);
user_pref(
  "browser.newtabpage.activity-stream.asrouter.userprefs.cfr.features",
  false
);

// Disable bookmark bar by default
user_pref("browser.toolbars.bookmarks.visibility", "never");
// Manjaro specific workaround
user_pref("distribution.Manjaro.bookmarksProcessed", true);

// Support for custom browser: protocol for opening links in main browser
user_pref("network.protocol-handler.expose.browser", false);
user_pref("security.external_protocol_requires_permission", false);

// Enable uBlock and extension for browser: protocol by default
user_pref(
  "extensions.webextensions.ExtensionStorageIDB.migrated.screenshots@mozilla.org",
  true
);
user_pref(
  "extensions.webextensions.ExtensionStorageIDB.migrated.uBlock0@raymondhill.net",
  true
);
