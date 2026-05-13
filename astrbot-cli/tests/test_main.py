"""Tests for main CLI module."""

import pytest
from typer.testing import CliRunner

from astrbot_cli.main import app


runner = CliRunner()


class TestMain:
    """Test main CLI entry point."""

    def test_repl_command_help(self):
        """Test repl command exists and has help."""
        result = runner.invoke(app, ["repl", "--help"])
        assert result.exit_code == 0

    def test_version_command(self):
        """Test version command exists."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0

    def test_unknown_command(self):
        """Test unknown command returns error."""
        result = runner.invoke(app, ["unknown-command"])
        assert result.exit_code != 0
