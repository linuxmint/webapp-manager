"""Tests for Wayland support in webapp-manager."""

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


class TestIsWaylandSession:
    """Tests for is_wayland_session() function."""

    def test_wayland_session_type(self, wayland_env):
        """Should return True when XDG_SESSION_TYPE is wayland."""
        assert common.is_wayland_session() is True

    def test_wayland_display_set(self):
        """Should return True when WAYLAND_DISPLAY is set."""
        with mock_environment(XDG_SESSION_TYPE="", WAYLAND_DISPLAY="wayland-0"):
            assert common.is_wayland_session() is True

    def test_x11_session(self, x11_env):
        """Should return False for X11 session."""
        assert common.is_wayland_session() is False

    def test_unset_environment(self, unset_env):
        """Should return False when environment variables are unset."""
        assert common.is_wayland_session() is False

    def test_wayland_session_type_case_insensitive(self):
        """Should handle case-insensitive session type."""
        with mock_environment(XDG_SESSION_TYPE="WAYLAND", WAYLAND_DISPLAY=None):
            assert common.is_wayland_session() is True

    def test_wayland_display_only(self):
        """Should detect Wayland from WAYLAND_DISPLAY alone."""
        with mock_environment(XDG_SESSION_TYPE="tty", WAYLAND_DISPLAY="wayland-1"):
            assert common.is_wayland_session() is True


class TestGetChromiumWaylandClass:
    """Tests for get_chromium_wayland_class() function."""

    def test_simple_url_isolated_profile(self):
        """Should generate correct class for simple URL with isolated profile."""
        result = common.get_chromium_wayland_class(
            url="https://calendar.google.com",
            custom_parameters="",
            isolate_profile=True
        )
        assert result == "chrome-calendar.google.com__-Default"

    def test_url_with_path(self):
        """Path should be included with slashes converted to underscores."""
        result = common.get_chromium_wayland_class(
            url="https://example.com/some/path/here",
            custom_parameters="",
            isolate_profile=True
        )
        assert result == "chrome-example.com__some_path_here-Default"

    def test_url_with_port(self):
        """Port should be stripped from domain, path included."""
        result = common.get_chromium_wayland_class(
            url="https://localhost:8080/app",
            custom_parameters="",
            isolate_profile=True
        )
        assert result == "chrome-localhost__app-Default"

    def test_custom_profile_with_equals(self):
        """Should extract profile from --profile-directory=ProfileName."""
        result = common.get_chromium_wayland_class(
            url="https://example.com",
            custom_parameters='--profile-directory="Profile 1"',
            isolate_profile=False
        )
        assert result == "chrome-example.com__-Profile_1"

    def test_custom_profile_with_space(self):
        """Should extract profile from --profile-directory ProfileName."""
        result = common.get_chromium_wayland_class(
            url="https://example.com",
            custom_parameters="--profile-directory 'My Profile'",
            isolate_profile=False
        )
        assert result == "chrome-example.com__-My_Profile"

    def test_profile_spaces_converted_to_underscores(self):
        """Spaces in profile names should be replaced with underscores."""
        result = common.get_chromium_wayland_class(
            url="https://example.com",
            custom_parameters='--profile-directory="Work Profile"',
            isolate_profile=False
        )
        assert result == "chrome-example.com__-Work_Profile"

    def test_subdomain_preserved(self):
        """Subdomains should be preserved in the class name."""
        result = common.get_chromium_wayland_class(
            url="https://mail.google.com",
            custom_parameters="",
            isolate_profile=True
        )
        assert result == "chrome-mail.google.com__-Default"

    def test_isolated_profile_ignores_custom_parameters(self):
        """When isolate_profile is True, custom profile directory is ignored."""
        result = common.get_chromium_wayland_class(
            url="https://example.com",
            custom_parameters='--profile-directory="Custom"',
            isolate_profile=True
        )
        assert result == "chrome-example.com__-Default"

    def test_http_url(self):
        """Should work with http:// URLs."""
        result = common.get_chromium_wayland_class(
            url="http://insecure.example.com",
            custom_parameters="",
            isolate_profile=True
        )
        assert result == "chrome-insecure.example.com__-Default"

    def test_empty_custom_parameters(self):
        """Should handle empty custom parameters gracefully."""
        result = common.get_chromium_wayland_class(
            url="https://example.com",
            custom_parameters="",
            isolate_profile=False
        )
        assert result == "chrome-example.com__-Default"

    def test_custom_parameters_without_profile(self):
        """Should use Default when custom params don't include profile."""
        result = common.get_chromium_wayland_class(
            url="https://example.com",
            custom_parameters="--disable-extensions --start-maximized",
            isolate_profile=False
        )
        assert result == "chrome-example.com__-Default"


class TestWaylandChromiumIntegration:
    """Tests for Wayland + Chromium behavior."""

    def test_wayland_chromium_uses_chrome_class(self):
        """On Wayland, Chromium browsers should use chrome-{domain}__-{profile} format."""
        with mock_environment(XDG_SESSION_TYPE="wayland", WAYLAND_DISPLAY="wayland-0"):
            codename = "TestApp1234"
            browser_type = common.BROWSER_TYPE_CHROMIUM
            url = "https://calendar.google.com"

            if common.is_wayland_session() and browser_type == common.BROWSER_TYPE_CHROMIUM:
                wm_class = common.get_chromium_wayland_class(url, "", True)
            else:
                wm_class = "WebApp-%s" % codename

            assert wm_class == "chrome-calendar.google.com__-Default"

    def test_wayland_chromium_with_custom_profile(self):
        """On Wayland, Chromium with custom profile should reflect in class."""
        with mock_environment(XDG_SESSION_TYPE="wayland", WAYLAND_DISPLAY="wayland-0"):
            codename = "WorkApp5678"
            browser_type = common.BROWSER_TYPE_CHROMIUM
            url = "https://docs.google.com"
            custom_params = '--profile-directory="Work Profile"'

            if common.is_wayland_session() and browser_type == common.BROWSER_TYPE_CHROMIUM:
                wm_class = common.get_chromium_wayland_class(url, custom_params, False)
            else:
                wm_class = "WebApp-%s" % codename

            assert wm_class == "chrome-docs.google.com__-Work_Profile"

    def test_chrome_prefix_detected_as_webapp(self):
        """Verify that 'chrome-' prefix is recognized as a webapp."""
        test_lines = [
            "StartupWMClass=chrome-calendar.google.com__-Default",
            "StartupWMClass=chrome-mail.google.com__-Profile_1",
            "StartupWMClass=chrome-localhost__-Default",
        ]

        for line in test_lines:
            is_webapp = ("StartupWMClass=WebApp" in line or
                        "StartupWMClass=Chromium" in line or
                        "StartupWMClass=ICE-SSB" in line or
                        "StartupWMClass=chrome-" in line)
            assert is_webapp is True, f"Failed to detect webapp for: {line}"
