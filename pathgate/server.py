import argparse
import asyncio
import os
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server

from pathgate import prompts, resources, tool_schemas, tools
from pathgate.config import configure


def _version() -> str:
    try:
        return version("pathgate")
    except PackageNotFoundError:
        return "0.0.0"


server = Server(
    "pathgate",
    version=_version(),
    on_list_tools=tool_schemas.list_tools,
    on_call_tool=tools.call_tool,
    on_list_resources=resources.list_resources,
    on_read_resource=resources.read_resource,
    on_list_prompts=prompts.list_prompts,
    on_get_prompt=prompts.get_prompt,
)


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="pathgate")
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


async def _run():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main():
    paths, read_only = parse_args()
    configure(paths, read_only)
    asyncio.run(_run())


if __name__ == "__main__":
    main()