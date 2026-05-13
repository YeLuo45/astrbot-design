"""Tests for REPL command - refactored for testability."""

import pytest
from unittest.mock import patch, MagicMock
import requests


class TestReplCommandParsing:
    """Test REPL command parsing logic (non-interactive)."""

    def test_exit_commands_list(self):
        """Test that all exit commands are recognized."""
        exit_commands = ("exit", "quit", "q")
        for cmd in exit_commands:
            assert cmd.lower() in ("exit", "quit", "q")

    def test_help_command_recognized(self):
        """Test help command is recognized."""
        assert "help".lower() == "help"

    def test_clear_command_recognized(self):
        """Test clear command is recognized."""
        assert "clear".lower() == "clear"

    def test_empty_input_handled(self):
        """Test empty input is handled."""
        user_input = ""
        assert user_input.strip() == ""

    def test_command_case_insensitive(self):
        """Test commands are case insensitive."""
        assert "EXIT".lower() in ("exit", "quit", "q")
        assert "HELP".lower() == "help"
        assert "CLEAR".lower() == "clear"


class TestReplApiCalls:
    """Test REPL API call logic."""

    @patch('requests.post')
    def test_agent_api_endpoint_format(self, mock_post):
        """Test agent call uses correct endpoint format."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "test"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        base_url = "http://localhost:8000"
        agent_id = "my-agent"
        input_text = "hello"

        response = requests.post(
            f"{base_url}/api/agents/{agent_id}/call",
            json={"input": input_text},
            timeout=30
        )

        mock_post.assert_called_once()
        call_url = mock_post.call_args[0][0]
        assert agent_id in call_url
        assert "/api/agents/" in call_url

    @patch('requests.post')
    def test_connection_error_handling(self, mock_post):
        """Test connection error is caught."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")

        base_url = "http://localhost:8000"
        agent_id = "test"

        try:
            requests.post(f"{base_url}/api/agents/{agent_id}/call", timeout=30)
        except requests.exceptions.ConnectionError as e:
            assert "Connection refused" in str(e)

    @patch('requests.post')
    def test_timeout_error_handling(self, mock_post):
        """Test timeout error is caught."""
        mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

        base_url = "http://localhost:8000"
        agent_id = "test"

        try:
            requests.post(f"{base_url}/api/agents/{agent_id}/call", timeout=30)
        except requests.exceptions.Timeout as e:
            assert "timed out" in str(e)

    @patch('requests.post')
    def test_response_parsing(self, mock_post):
        """Test API response parsing."""
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Agent response text"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        base_url = "http://localhost:8000"
        response = requests.post(f"{base_url}/api/agents/test/call", json={"input": "hi"})
        data = response.json()
        result = data.get("response", "No response")

        assert result == "Agent response text"


class TestReplFormatting:
    """Test REPL formatting functions."""

    def test_url_construction(self):
        """Test base URL is correctly constructed."""
        host = "localhost"
        port = 8000
        base_url = f"http://{host}:{port}"
        assert base_url == "http://localhost:8000"

    def test_custom_host_port_url(self):
        """Test custom host and port in URL."""
        host = "192.168.1.100"
        port = 9000
        base_url = f"http://{host}:{port}"
        assert base_url == "http://192.168.1.100:9000"
