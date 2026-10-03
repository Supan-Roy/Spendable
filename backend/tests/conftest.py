"""Pytest configuration and global session fixtures.

Guarantees zero Gemini API credit consumption during test execution.
"""

import os
import pytest


@pytest.fixture(autouse=True)
def disable_gemini_api_during_tests(monkeypatch):
    """Global autouse fixture ensuring pytest test runs NEVER call live Gemini API endpoints or waste API credits."""
    monkeypatch.setenv("GEMINI_API_KEY", "")
