'use strict'

function isValidUrl(url) {
  try {
    new URL(url)
    return true
  } catch (err) {
    return false
  }
}

const isSameDomain = (url) =>
  new URL(url).hostname === new URL(window.location.href).hostname

function clickHandler(e) {
  // TODO: What if the element is a child of an <a> tag?
  if (e.target.tagName !== 'A' || !e.target.hasAttribute('href')) return

  // If the site is already preventing the default then we shouldn't do anything
  if (e.defaultPrevented) return

  const url = e.target.getAttribute('href')
  if (!isValidUrl(url)) return
  if (isSameDomain(url)) return

  // Prevent the <a> tag from opening the url so we can handle
  e.preventDefault()

  // Open the url with our custom protocol and immediately close
  // Use an <a> tag over window.open because it prevents a temp tab
  const aElem = document.createElement('a')
  aElem.href = 'browser:' + url
  aElem.click()
}

window.addEventListener('click', clickHandler)
setInterval(() => {
  window.removeEventListener('click', clickHandler)
  window.addEventListener('click', clickHandler)
}, 100)

const windowOpen = window.open
const wrappedWindowOpen = (...args) => {
  const url = args[0]
  if (
    typeof url !== 'string' ||
    url.startsWith('browser:') ||
    !isValidUrl(url)
  ) {
    return windowOpen.call(window, ...args)
  }
  return windowOpen.call(window, 'browser:' + url, ...args.slice(1)).close()
}

window.open = wrappedWindowOpen
setInterval(() => {
  if (window.open === wrappedWindowOpen) return
  window.open = wrappedWindowOpen
}, 100)
