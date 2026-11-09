from pathgate.config import configure, server
from mcp.server.stdio import stdio_server
from pathgate import tools, resources, prompts, tool_schemas
import asyncio
import os
import argparse
from pathlib import Path

server.list_tools()(tool_schemas.list_tools)
server.call_tool()(tools.call_tool)
server.list_resources()(resources.list_resources)
server.read_resource()(resources.read_resource)
server.list_prompts()(prompts.list_prompts)
server.get_prompt()(prompts.get_prompt)

def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="filesystem-mcp-server")
    p.add_argument("paths", nargs="*", help="Directories the server may access")
    p.add_argument("--read-only", action="store_true", help="Disable write/delete/move/copy tools")
    args = p.parse_args(argv)

    env_paths = [x for x in os.environ.get("FS_MCP_ALLOWED_PATHS", "").split(os.pathsep) if x]
    raw = args.paths or env_paths
    if not raw:
        p.error("no allowed directories given. Pass at least one path "
                "or set FS_MCP_ALLOWED_PATHS.")

    paths = [str(Path(x).expanduser().resolve()) for x in raw]
    for x in paths:
        if not Path(x).is_dir():
            p.error(f"not a directory: {x}")
    return paths, args.read_only

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    paths, read_only = parse_args()
    configure(paths, read_only)
    asyncio.run(main())

