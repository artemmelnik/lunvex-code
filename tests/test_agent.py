"""Tests for agent permission handling."""

from unittest.mock import patch

from lunvex_code.agent import Agent
from lunvex_code.llm import ToolCall
from lunvex_code.permissions import PermissionLevel, PermissionManager, PermissionRequest
from lunvex_code.tools.base import ToolRegistry
from lunvex_code.tools.file_tools import WriteFileTool


class TestAgentPermissionHandling:
    """Test cases for agent permission prompts."""

    def _make_agent(self) -> Agent:
        """Create a lightweight agent instance for permission tests."""
        agent = Agent.__new__(Agent)
        agent.permissions = PermissionManager()
        return agent

    def test_write_file_always_adds_tool_wide_allowlist(self):
        """Choosing always for write_file should allow future write_file calls."""
        agent = self._make_agent()
        request = PermissionRequest(
            tool_name="write_file",
            tool_input={"path": "/tmp/first.txt", "content": "hello"},
            level=PermissionLevel.ASK,
        )

        with patch("lunvex_code.agent.ui.ask_permission", return_value="always"):
            with patch("lunvex_code.agent.ui.print_info") as mock_print_info:
                allowed = agent._get_permission(request)

        assert allowed is True
        assert "write_file(*)" in agent.permissions.session_rule.allowlist
        mock_print_info.assert_called_once_with("Added 'write_file(*)' to session allowlist")

        follow_up_request = agent.permissions.check_permission(
            "write_file", {"path": "/tmp/second.txt", "content": "world"}
        )
        assert follow_up_request.level == PermissionLevel.AUTO

    def test_edit_file_always_adds_tool_wide_allowlist(self):
        """Choosing always for edit_file should allow future edit_file calls."""
        agent = self._make_agent()
        request = PermissionRequest(
            tool_name="edit_file",
            tool_input={"path": "/tmp/first.txt", "old_str": "a", "new_str": "b"},
            level=PermissionLevel.ASK,
        )

        with patch("lunvex_code.agent.ui.ask_permission", return_value="always"):
            with patch("lunvex_code.agent.ui.print_info") as mock_print_info:
                allowed = agent._get_permission(request)

        assert allowed is True
        assert "edit_file(*)" in agent.permissions.session_rule.allowlist
        mock_print_info.assert_called_once_with("Added 'edit_file(*)' to session allowlist")

        follow_up_request = agent.permissions.check_permission(
            "edit_file", {"path": "/tmp/second.txt", "old_str": "x", "new_str": "y"}
        )
        assert follow_up_request.level == PermissionLevel.AUTO

    def test_execute_tool_rejects_raw_arguments_before_permission_prompt(self):
        """Malformed tool arguments should not reach the tool implementation."""
        agent = self._make_agent()
        registry = ToolRegistry()
        registry.register(WriteFileTool())
        agent.registry = registry

        tool_call = ToolCall(
            id="call_1",
            name="write_file",
            arguments={"raw": '{"path":"ContactSection.tsx", content:"broken"}'},
        )

        with patch.object(agent, "_get_permission") as mock_get_permission:
            result = agent._execute_tool(tool_call)

        assert "Invalid tool arguments for 'write_file'" in result
        assert "Expected keys: path, content" in result
        mock_get_permission.assert_not_called()
