#!/bin/bash
# !!! For development you can load the extension on about:debugging as a temporary addon
# by pointing it to the manifest.json instead of signing the whole extension

# For production, you need to sign the firefox extension using the `web-ext` package
# You can acquire credentials for signing here: https://addons.mozilla.org/en-US/developers/addon/api/key/
# https://stackoverflow.com/questions/34608873/how-to-sign-a-firefox-extension
set -e

web-ext sign -s firefox-extension --api-key YOUR_API_KEY --api-secret YOUR_API_SECRET
mv web-ext-artifacts/* firefox-extension.xpi
rm -r web-ext-artifacts
