const newTabIds = []

// On create, we don't know the URL of the tab so we return focus to the
// original tab and add the tabId to the list of new tabs. Once we know the URL,
// we can either focus it or redirect it to the main browser
browser.tabs.onCreated.addListener((tab) => {
  if (tab.url !== 'about:blank') return
  browser.tabs.update(1, { active: true })
  newTabIds.push(tab.id)
})

// What about login through google or something like that?
browser.tabs.onUpdated.addListener((tabId, { url }) => {
  // URL didn't change so ignore
  if (!url) return

  // Find out if it's a new tab from the array filled by onCreated
  const isNewTab = newTabIds.includes(tabId)
  if (isNewTab) newTabIds.splice(newTabIds.indexOf(tabId), 1)

  // If it's id 1 then it's the main tab so ignore
  if (tabId === 1) return

  // Allow anything that isnt http or https. E.x. about:config
  if (!url.startsWith('http:') && !url.startsWith('https:')) {
    // New tab and we aren't redirecting it so focus it instead
    if (isNewTab && !url.startsWith('browser:')) {
      browser.tabs.update(tabId, { active: true })
    }
    return
  }

  // Remove and create tab with browser: prefix to redirect to main browser
  browser.tabs.remove(tabId)
  browser.tabs
    .create({ url: 'browser:' + url, active: false })
    // Delete the tab a 3s after
    .then((newTab) => setTimeout(() => browser.tabs.remove(newTab.id), 3000))
})

