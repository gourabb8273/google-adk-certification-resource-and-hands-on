"""
File Reader Assistant Agent

Demonstrates MCP tools integration with ADK using the filesystem MCP server.

Reference: https://google.github.io/adk-docs/tools-custom/mcp-tools/
MCP registry: https://registry.modelcontextprotocol.io
"""

from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
# Remote/production alternative:
# from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from mcp import StdioServerParameters

load_dotenv(Path(__file__).parent / ".env")

# Absolute path required by the filesystem MCP server
ALLOWED_PATH = str((Path(__file__).parent / "my_files").resolve())
Path(ALLOWED_PATH).mkdir(parents=True, exist_ok=True)

root_agent = LlmAgent(
    model="gemini-3.6-flash",
    name="file_reader_assistant",
    description="Reads and lists files via MCP filesystem tools.",
    instruction="""You are a file reader assistant that helps users explore files.

Your capabilities:
- List files in directories using list_directory
- Read file contents using read_file

When helping users:
1. Use list_directory to show available files
2. Use read_file to display file contents when asked
3. Describe what you find in a helpful way

Always be clear about which folder you're working with.""",
    tools=[
        # StdioConnectionParams — local subprocess (development)
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-filesystem",
                        ALLOWED_PATH,
                    ],
                ),
            ),
            tool_filter=["read_file", "list_directory"],
        )
        # SseConnectionParams — remote HTTP (production), e.g.:
        # McpToolset(
        #     connection_params=SseConnectionParams(
        #         url="https://your-mcp-server.example.com/sse",
        #     ),
        #     tool_filter=["read_file", "list_directory"],
        # )
    ],
)
