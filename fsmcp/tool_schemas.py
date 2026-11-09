from fsmcp.config import server
from mcp.types import Tool, ListToolsResult

@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools"""
    tools = [
        Tool(
            name="read_file_tool",
            description="Read the contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string", 
                        "description": "Absolute or relative path to the file"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="write_file_tool",
            description="Write content to a file (creates or overwrites)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the file"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write"
                    },
                    "encoding": {
                        "type": "string",
                        "description": "File encoding (default: utf-8)",
                        "default": "utf-8"
                    }
                },
                "required": ["path", "content"]
            }
        ),
        Tool(
            name="list_directory_tool",
            description="List contents of a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the directory"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "If True, list subdirectories recursively",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="create_directory_tool",
            description="Create a new directory (creates parent directories if needed)",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the directory"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="delete_file_tool",
            description="Delete a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the file"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="delete_directory_tool",
            description="Delete a directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the directory"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "If True, delete directory and all contents",
                        "default": False
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="move_file_tool",
            description="Move or rename a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source path"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination path"
                    }
                },
                "required": ["source", "destination"]
            }
        ),
        Tool(
            name="copy_file_tool",
            description="Copy a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": "Source path"
                    },
                    "destination": {
                        "type": "string",
                        "description": "Destination path"
                    }
                },
                "required": ["source", "destination"]
            }
        ),
        Tool(
            name="search_files_tool",
            description="Search for files matching a pattern",
            inputSchema={
                "type": "object",
                "properties": {
                    "directory": {
                        "type": "string",
                        "description": "Directory to search in"
                    },
                    "pattern": {
                        "type": "string",
                        "description": "Filename pattern (supports wildcards like *.txt)"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "If True, search subdirectories",
                        "default": True
                    }
                },
                "required": ["directory", "pattern"]
            }
        ),
        Tool(
            name="get_file_info_tool",
            description="Get detailed information about a file or directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path"
                    }
                },
                "required": ["path"]
            }
        )
    ]
    
    return ListToolsResult(tools=tools)
