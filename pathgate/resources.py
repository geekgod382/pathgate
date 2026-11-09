import json
import os

from mcp import MCPError
from mcp.server import ServerRequestContext
from mcp.types import (INVALID_PARAMS, ListResourcesResult, PaginatedRequestParams,
                       ReadResourceRequestParams, ReadResourceResult, Resource,
                       TextResourceContents)

from pathgate.config import is_path_allowed


async def list_resources(ctx: ServerRequestContext, params: PaginatedRequestParams | None) -> ListResourcesResult:
    return ListResourcesResult(resources=[
        Resource(uri="file://*", name="File Contents",
                 description="Read the contents of any file by providing its path",
                 mime_type="text/plain"),
        Resource(uri="directory://*", name="Directory Listing",
                 description="List the contents of any directory by providing its path",
                 mime_type="application/json"),
    ])


async def read_resource(ctx: ServerRequestContext, params: ReadResourceRequestParams) -> ReadResourceResult:
    uri = params.uri

    if uri.startswith("file://"):
        path = uri[len("file://"):]
        if not is_path_allowed(path):
            raise MCPError(INVALID_PARAMS, f"Access denied to {path}")
        if not os.path.isfile(path):
            raise MCPError(INVALID_PARAMS, f"File not found or not a file: {path}")
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        return ReadResourceResult(contents=[
            TextResourceContents(uri=uri, text=text, mime_type="text/plain")])

    if uri.startswith("directory://"):
        path = uri[len("directory://"):]
        if not is_path_allowed(path):
            raise MCPError(INVALID_PARAMS, f"Access denied to {path}")
        if not os.path.isdir(path):
            raise MCPError(INVALID_PARAMS, f"Directory not found: {path}")
        entries = []
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            stat = os.stat(item_path)
            entries.append({"name": item,
                            "type": "directory" if os.path.isdir(item_path) else "file",
                            "size": stat.st_size, "modified": stat.st_mtime})
        return ReadResourceResult(contents=[
            TextResourceContents(uri=uri, text=json.dumps(entries, indent=2),
                                 mime_type="application/json")])

    raise MCPError(INVALID_PARAMS, f"Unsupported resource URI: {uri}")