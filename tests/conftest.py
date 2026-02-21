"""Pytest configuration and fixtures for webapp-manager tests."""

import os
import sys
from contextlib import contextmanager

import pytest

# Add webapp-manager library to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "usr", "lib", "webapp-manager"))


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


@pytest.fixture
def wayland_env():
    """Fixture to simulate a Wayland session environment."""
    with mock_environment(XDG_SESSION_TYPE="wayland", WAYLAND_DISPLAY="wayland-0"):
        yield


@pytest.fixture
def x11_env():
    """Fixture to simulate an X11 session environment."""
    with mock_environment(XDG_SESSION_TYPE="x11", WAYLAND_DISPLAY=None):
        yield


@pytest.fixture
def unset_env():
    """Fixture with display environment variables unset."""
    with mock_environment(XDG_SESSION_TYPE=None, WAYLAND_DISPLAY=None):
        yield
