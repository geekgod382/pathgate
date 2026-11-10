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

Pathgate package is published on PyPI. To use it, for example with Claude Desktop, add this in the 

```json
{
  "mcpServers": {
    "pathgate": {
      "command": "uvx",
      "args": ["pathgate@latest", "C:\\Users\\me\\Documents"]
    }
  }
}
```

Or, you can use the install command to directly write the config file

```bash
uvx pathgate install <paths>
```

paths should have nothing between them

```bash
uvx pathgate install C:\Users\me\Documents C:\Users\me\Projects
```

When no paths are given, it prompts you for them.

### Options

`--read-only:` writes the safer variant of the entry.
`--dry-run`: shows what it would write and changes nothing.
`--yes`: skips the confirmation prompt.
`--name`: sets a different entry name (default pathgate).
`--config PATH`: I build this mcp server for Claude primarily. Using this option edits a specific file, which also works for other clients that use the same mcpServers shape.

### Updating

You don't need to manually update it. The command does that for you.

## Usage

### Start with allowed directories

```bash
uvx pathgate "C:\Users\<username>\Documents" "C:\Users\<username>\Projects"
```

### Read-only mode

```bash
uvx pathgate --read-only "C:\Users\<username>\Documents"
```

### Environment variable alternative

```bash
$env:FS_MCP_ALLOWED_PATHS = "C:\Users\<username>\Documents;C:\Users\<username>\Projects"
uvx pathgate
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
pathgate/
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
- `mcp>=2`

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Python SDK](https://github.com/modelcontextprotocol/python-sdk)