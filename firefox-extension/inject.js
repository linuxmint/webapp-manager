const injectScript = () => {
  const scriptElem = document.createElement('script')
  scriptElem.src = browser.runtime.getURL('script.js')
  document.head.appendChild(scriptElem)
}

if (document.readyState === 'interactive') injectScript()
else window.addEventListener('load', injectScript)
