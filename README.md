# Pathgate

`pathgate` is a Python Model Context Protocol (MCP) server that exposes a controlled filesystem interface to MCP clients such as Claude Desktop, Cursor, VS Code, and inspector tools. The server only permits access to directories that are explicitly allow-listed at startup.

## What it does

The server exposes:

- File resources via `file://...`
- Directory resources via `directory://...`
- Tools for reading, writing, listing, creating, deleting, moving, copying, searching, and inspecting files/directories
- Built-in prompts for directory analysis and file discovery

## Security model

Access is restricted by allow-listed paths. At startup, the server resolves the supplied paths and only permits operations within those directories.

- Paths are checked with `os.path.realpath()` and prefix matching
- Symlinks are resolved before comparison
- The server can be run in read-only mode to disable mutating operations

## Installation

```bash
git clone https://github.com/geekgod382/filesystem-mcp-server.git
cd filesystem-mcp-server
python -m pip install -e .
```

This installs the `filesystem-mcp-server` console command from `pyproject.toml`.

## Usage

### Start with allowed directories

```bash
filesystem-mcp-server "C:\Users\<username>\Documents" "C:\Users\<username>\Projects"
```

### Read-only mode

```bash
filesystem-mcp-server --read-only "C:\Users\<username>\Documents"
```

### Environment variable alternative

```bash
$env:FS_MCP_ALLOWED_PATHS = "C:\Users\<username>\Documents;C:\Users\<username>\Projects"
filesystem-mcp-server
```

On macOS/Linux, use `:` instead of `;` for the path separator.

## Tools

The current implementation exposes these tools:

- `read_file_tool` — read a file and return its content, size, and encoding
- `write_file_tool` — write content to a file
- `list_directory_tool` — list directory contents, optionally recursively
- `create_directory_tool` — create a directory tree if needed
- `delete_file_tool` — delete a single file
- `delete_directory_tool` — delete a directory, optionally recursively
- `move_file_tool` — move or rename a file/directory
- `copy_file_tool` — copy a file/directory
- `search_files_tool` — search for files matching a pattern
- `get_file_info_tool` — return metadata for a file or directory

## MCP client configuration

Example Claude Desktop configuration:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "filesystem-mcp-server",
      "args": ["C:\\Users\\<username>\\Documents"]
    }
  }
}
```

## Example requests

Once connected, clients can ask:

```text
List the files in C:\Users\<username>\Documents
```

```text
Read C:\Users\<username>\Documents\notes.txt
```

```text
Search for *.py files under C:\Users\<username>\Projects
```

```text
Create a file at C:\Users\<username>\Documents\todo.txt with the content "Ship release"
```

## Project layout

```text
filesystem-mcp-server/
├── pathgate/
│   ├── __init__.py
│   ├── __main__.py
│   ├── config.py
│   ├── prompts.py
│   ├── resources.py
│   ├── server.py
│   ├── tool_schemas.py
│   └── tools.py
├── tests/
│   └── test_server.py
├── pyproject.toml
├── README.md
└── LICENSE
```

## Requirements

- Python 3.10+
- `mcp>=1.25`

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)