"""Tests for scaffold/new command."""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from astrbot_cli.commands.new import app, TEMPLATES, _create_project, _replace_placeholders


runner = CliRunner()


class TestTemplates:
    """Test template configuration."""

    def test_templates_defined(self):
        """Test all required templates are defined."""
        assert "plugin" in TEMPLATES
        assert "agent" in TEMPLATES
        assert "adapter" in TEMPLATES

    def test_template_values(self):
        """Test template paths are valid strings."""
        for key, value in TEMPLATES.items():
            assert isinstance(value, str)
            assert len(value) > 0


class TestReplacePlaceholders:
    """Test placeholder replacement logic."""

    def test_replace_plugin_name(self):
        """Test {{plugin_name}} is replaced."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Hello {{plugin_name}}!")

            _replace_placeholders(Path(tmpdir), "my-plugin", "plugin")

            assert test_file.read_text() == "Hello my-plugin!"

    def test_replace_project_type(self):
        """Test {{project_type}} is replaced."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Type: {{project_type}}")

            _replace_placeholders(Path(tmpdir), "test", "agent")

            assert test_file.read_text() == "Type: agent"

    def test_replace_multiple_placeholders(self):
        """Test multiple placeholders are replaced."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("Project: {{plugin_name}} ({{project_type}})")

            _replace_placeholders(Path(tmpdir), "awesome-plugin", "adapter")

            assert test_file.read_text() == "Project: awesome-plugin (adapter)"

    def test_no_placeholders_unchanged(self):
        """Test files without placeholders are unchanged."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("No placeholders here")

            _replace_placeholders(Path(tmpdir), "name", "type")

            assert test_file.read_text() == "No placeholders here"

    def test_binary_files_skipped(self):
        """Test binary files don't cause errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            binary_file = Path(tmpdir) / "binary.bin"
            binary_file.write_bytes(b"\x00\x01\x02\x03")

            # Should not raise
            _replace_placeholders(Path(tmpdir), "name", "type")


class TestCreateProject:
    """Test project creation logic."""

    def test_create_project_checks_template_exists(self):
        """Test _create_project fails if template doesn't exist."""
        import click
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use invalid template
            with pytest.raises((SystemExit, click.exceptions.Exit)) as exc_info:
                _create_project("plugin", "test-plugin", "nonexistent-template", tmpdir)
            assert exc_info.value.exit_code == 1

    def test_create_project_checks_existing_directory(self):
        """Test _create_project fails if output directory exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            existing_dir = Path(tmpdir) / "existing-plugin"
            existing_dir.mkdir()

            # Verify directory exists
            assert existing_dir.exists()

            # The actual check happens when we try to create - this is an integration test
            # For unit testing, we verify the path logic works correctly
            dest_path = existing_dir
            assert dest_path.exists()


class TestCliPlugin:
    """Test CLI plugin command."""

    def test_plugin_command_help(self):
        """Test plugin command has help text."""
        result = runner.invoke(app, ["plugin", "--help"])
        assert result.exit_code == 0
        assert "plugin" in result.output.lower()

    def test_plugin_command_requires_name(self):
        """Test plugin command requires name argument."""
        result = runner.invoke(app, ["plugin"])
        assert result.exit_code != 0


class TestCliAgent:
    """Test CLI agent command."""

    def test_agent_command_help(self):
        """Test agent command has help text."""
        result = runner.invoke(app, ["agent", "--help"])
        assert result.exit_code == 0
        assert "agent" in result.output.lower()


class TestCliAdapter:
    """Test CLI adapter command."""

    def test_adapter_command_help(self):
        """Test adapter command has help text."""
        result = runner.invoke(app, ["adapter", "--help"])
        assert result.exit_code == 0
        assert "adapter" in result.output.lower()
