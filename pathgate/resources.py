from pathgate.config import server, is_path_allowed
from mcp.types import (Resource, ListResourcesResult, ReadResourceResult, TextContent)
import os
import json

# RESOURCES HANDLERS
@server.list_resources()
async def list_resources() -> ListResourcesResult:
    """List available resources"""
    resources = [
        Resource(
            uri="file://*",
            name="File Contents",
            description="Read the contents of any file by providing its path",
            mimeType="text/plain"
        ),
        Resource(
            uri="directory://*",
            name="Directory Listing",
            description="List the contents of any directory by providing its path",
            mimeType="application/json"
        )
    ]
    
    return ListResourcesResult(resources=resources)

@server.read_resource()
async def read_resource(uri: str) -> ReadResourceResult:
    """Read a resource"""
    if uri.startswith("file://"):
        path = uri[7:]  # Remove "file://" prefix
        
        if not is_path_allowed(path):
            return ReadResourceResult(
                contents=[TextContent(type="text", text=f"Error: Access denied to {path}")]
            )
        
        if not os.path.exists(path) or not os.path.isfile(path):
            return ReadResourceResult(
                contents=[TextContent(type="text", text=f"Error: File not found or not a file: {path}")]
            )
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return ReadResourceResult(
                contents=[TextContent(type="text", text=content)]
            )
        except Exception as e:
            return ReadResourceResult(
                contents=[TextContent(type="text", text=f"Error reading file: {str(e)}")]
            )
    
    elif uri.startswith("directory://"):
        path = uri[12:]  # Remove "directory://" prefix
        
        if not is_path_allowed(path):
            return ReadResourceResult(
                contents=[TextContent(type="text", text=f"Error: Access denied to {path}")]
            )
        
        if not os.path.exists(path) or not os.path.isdir(path):
            return ReadResourceResult(
                contents=[TextContent(type="text", text=f"Error: Directory not found or not a directory: {path}")]
            )
        
        try:
            entries = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                stat = os.stat(item_path)
                entries.append({
                    "name": item,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
            
            return ReadResourceResult(
                contents=[TextContent(type="text", text=json.dumps(entries, indent=2))]
            )
        except Exception as e:
            return ReadResourceResult(
                contents=[TextContent(type="text", text=f"Error listing directory: {str(e)}")]
            )
    
    else:
        return ReadResourceResult(
            contents=[TextContent(type="text", text="Error: Unsupported resource URI")]
        )
