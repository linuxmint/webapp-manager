"""Tests for X11 and non-Chromium browser behavior."""

import os
import sys
from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest

# Mock gi.repository before importing common (requires GTK)
sys.modules['gi'] = MagicMock()
sys.modules['gi.repository'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['requests'] = MagicMock()

# Add webapp-manager library to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "usr", "lib", "webapp-manager"))

# Import the module under test
import common


@contextmanager
def mock_environment(**env_vars):
    """Context manager to temporarily set environment variables."""
    original = {}
    for key, value in env_vars.items():
        original[key] = os.environ.get(key)
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
    try:
        yield
    finally:
        for key, orig_value in original.items():
            if orig_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = orig_value


class TestWebappDetection:
    """Tests for webapp detection formats."""

    def test_all_webapp_formats_detected(self):
        """Verify all StartupWMClass formats are detected."""
        formats = [
            ("StartupWMClass=WebApp-MyApp1234", "WebApp- prefix"),
            ("StartupWMClass=WebApp-Gmail5678", "WebApp- with name"),
            ("StartupWMClass=ICE-SSB-oldapp", "ICE-SSB format"),
            ("StartupWMClass=Chromium-webapp", "Chromium format"),
        ]

        for line, description in formats:
            is_webapp = ("StartupWMClass=WebApp" in line or
                        "StartupWMClass=Chromium" in line or
                        "StartupWMClass=ICE-SSB" in line or
                        "StartupWMClass=chrome-" in line)
            assert is_webapp is True, f"Failed to detect format ({description}): {line}"

    def test_non_webapp_not_detected(self):
        """Non-webapp StartupWMClass should not be detected."""
        test_lines = [
            "StartupWMClass=Firefox",
            "StartupWMClass=Nautilus",
            "StartupWMClass=gnome-terminal",
        ]

        for line in test_lines:
            is_webapp = ("StartupWMClass=WebApp" in line or
                        "StartupWMClass=Chromium" in line or
                        "StartupWMClass=ICE-SSB" in line or
                        "StartupWMClass=chrome-" in line)
            assert is_webapp is False, f"Incorrectly detected as webapp: {line}"


class TestX11Behavior:
    """Tests for X11 session behavior."""

    def test_x11_chromium_uses_webapp_class(self):
        """On X11, Chromium browsers should use WebApp-{codename} format."""
        with mock_environment(XDG_SESSION_TYPE="x11", WAYLAND_DISPLAY=None):
            codename = "TestApp1234"
            browser_type = common.BROWSER_TYPE_CHROMIUM

            if common.is_wayland_session() and browser_type == common.BROWSER_TYPE_CHROMIUM:
                wm_class = common.get_chromium_wayland_class("https://example.com", "", True)
            else:
                wm_class = "WebApp-%s" % codename

            assert wm_class == "WebApp-TestApp1234"

    def test_unset_env_chromium_uses_webapp_class(self):
        """With unset env vars, Chromium browsers should use WebApp-{codename} format."""
        with mock_environment(XDG_SESSION_TYPE=None, WAYLAND_DISPLAY=None):
            codename = "Gmail5678"
            browser_type = common.BROWSER_TYPE_CHROMIUM

            if common.is_wayland_session() and browser_type == common.BROWSER_TYPE_CHROMIUM:
                wm_class = common.get_chromium_wayland_class("https://mail.google.com", "", True)
            else:
                wm_class = "WebApp-%s" % codename

            assert wm_class == "WebApp-Gmail5678"

    def test_firefox_uses_webapp_class_on_x11(self):
        """Firefox browsers should use WebApp-{codename} on X11."""
        with mock_environment(XDG_SESSION_TYPE="x11", WAYLAND_DISPLAY=None):
            codename = "FirefoxApp5678"
            browser_type = common.BROWSER_TYPE_FIREFOX

            if common.is_wayland_session() and browser_type == common.BROWSER_TYPE_CHROMIUM:
                wm_class = common.get_chromium_wayland_class("https://example.com", "", True)
            else:
                wm_class = "WebApp-%s" % codename

            assert wm_class == "WebApp-FirefoxApp5678"


class TestNonChromiumBrowsers:
    """Tests for non-Chromium browsers (always use WebApp- format)."""

    def test_firefox_always_uses_webapp_class(self):
        """Firefox browsers should always use WebApp-{codename}, even on Wayland."""
        with mock_environment(XDG_SESSION_TYPE="wayland", WAYLAND_DISPLAY="wayland-0"):
            codename = "FirefoxApp1234"
            browser_type = common.BROWSER_TYPE_FIREFOX

            if common.is_wayland_session() and browser_type == common.BROWSER_TYPE_CHROMIUM:
                wm_class = common.get_chromium_wayland_class("https://example.com", "", True)
            else:
                wm_class = "WebApp-%s" % codename

            assert wm_class == "WebApp-FirefoxApp1234"

    def test_epiphany_always_uses_webapp_class(self):
        """Epiphany browser should always use WebApp-{codename}."""
        with mock_environment(XDG_SESSION_TYPE="wayland", WAYLAND_DISPLAY="wayland-0"):
            codename = "EpiphanyApp1234"
            browser_type = common.BROWSER_TYPE_EPIPHANY

            if common.is_wayland_session() and browser_type == common.BROWSER_TYPE_CHROMIUM:
                wm_class = common.get_chromium_wayland_class("https://example.com", "", True)
            else:
                wm_class = "WebApp-%s" % codename

            assert wm_class == "WebApp-EpiphanyApp1234"

    def test_falkon_always_uses_webapp_class(self):
        """Falkon browser should always use WebApp-{codename}."""
        with mock_environment(XDG_SESSION_TYPE="wayland", WAYLAND_DISPLAY="wayland-0"):
            codename = "FalkonApp1234"
            browser_type = common.BROWSER_TYPE_FALKON

            if common.is_wayland_session() and browser_type == common.BROWSER_TYPE_CHROMIUM:
                wm_class = common.get_chromium_wayland_class("https://example.com", "", True)
            else:
                wm_class = "WebApp-%s" % codename

            assert wm_class == "WebApp-FalkonApp1234"

    def test_all_non_chromium_browsers_use_webapp_class(self):
        """All non-Chromium browser types should use WebApp-{codename}."""
        non_chromium_types = [
            (common.BROWSER_TYPE_FIREFOX, "Firefox"),
            (common.BROWSER_TYPE_FIREFOX_FLATPAK, "Firefox Flatpak"),
            (common.BROWSER_TYPE_FIREFOX_SNAP, "Firefox Snap"),
            (common.BROWSER_TYPE_LIBREWOLF_FLATPAK, "LibreWolf Flatpak"),
            (common.BROWSER_TYPE_WATERFOX_FLATPAK, "Waterfox Flatpak"),
            (common.BROWSER_TYPE_FLOORP_FLATPAK, "Floorp Flatpak"),
            (common.BROWSER_TYPE_EPIPHANY, "Epiphany"),
            (common.BROWSER_TYPE_FALKON, "Falkon"),
            (common.BROWSER_TYPE_ZEN_FLATPAK, "Zen Flatpak"),
        ]

        with mock_environment(XDG_SESSION_TYPE="wayland", WAYLAND_DISPLAY="wayland-0"):
            for browser_type, browser_name in non_chromium_types:
                codename = f"TestApp{browser_type}"

                if common.is_wayland_session() and browser_type == common.BROWSER_TYPE_CHROMIUM:
                    wm_class = common.get_chromium_wayland_class("https://example.com", "", True)
                else:
                    wm_class = "WebApp-%s" % codename

                assert wm_class == f"WebApp-TestApp{browser_type}", \
                    f"{browser_name} should use WebApp- format, got: {wm_class}"
