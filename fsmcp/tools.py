from mcp.types import (TextContent, CallToolResult)
import os
from fsmcp.config import is_path_allowed, server, is_read_only
import logging
import json
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    """Handle tool calls"""
    try:
        if name == "read_file_tool":
            return await read_file_tool(arguments)
        elif name == "write_file_tool":
            return await write_file_tool(arguments)
        elif name == "list_directory_tool":
            return await list_directory_tool(arguments)
        elif name == "create_directory_tool":
            return await create_directory_tool(arguments)
        elif name == "delete_file_tool":
            return await delete_file_tool(arguments)
        elif name == "delete_directory_tool":
            return await delete_directory_tool(arguments)
        elif name == "move_file_tool":
            return await move_file_tool(arguments)
        elif name == "copy_file_tool":
            return await copy_file_tool(arguments)
        elif name == "search_files_tool":
            return await search_files_tool(arguments)
        elif name == "get_file_info_tool":
            return await get_file_info_tool(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
    except Exception as e:
        logger.error(f"Error in {name}: {str(e)}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

# Tool implementations
async def read_file_tool(arguments: dict) -> CallToolResult:
    """Read the contents of a file"""
    path = arguments["path"]
    encoding = arguments.get("encoding", "utf-8")
    
    if not is_path_allowed(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {path}")]
        )
    
    if not os.path.exists(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: File not found: {path}")]
        )
    
    if not os.path.isfile(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Not a file: {path}")]
        )
    
    try:
        with open(path, 'r', encoding=encoding) as f:
            content = f.read()
        
        result = {
            "path": path,
            "content": content,
            "size": len(content),
            "encoding": encoding
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except UnicodeDecodeError:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Cannot decode file with {encoding} encoding")]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error reading file: {str(e)}")]
        )

async def write_file_tool(arguments: dict) -> CallToolResult:
    """Write content to a file"""
    path = arguments["path"]
    content = arguments["content"]
    encoding = arguments.get("encoding", "utf-8")

    iro = is_read_only()
    if not iro:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Write operations are disabled in read-only mode.")]
        )
    
    if not is_path_allowed(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {path}")]
        )
    
    try:
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        
        with open(path, 'w', encoding=encoding) as f:
            f.write(content)
        
        result = {
            "success": True,
            "path": path,
            "bytes_written": len(content.encode(encoding))
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error writing file: {str(e)}")]
        )

async def list_directory_tool(arguments: dict) -> CallToolResult:
    """List contents of a directory"""
    path = arguments["path"]
    recursive = arguments.get("recursive", False)
    
    if not is_path_allowed(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {path}")]
        )
    
    if not os.path.exists(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Directory not found: {path}")]
        )
    
    if not os.path.isdir(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Not a directory: {path}")]
        )
    
    try:
        entries = []
        
        if recursive:
            for root, dirs, files in os.walk(path):
                for name in dirs + files:
                    item_path = os.path.join(root, name)
                    stat = os.stat(item_path)
                    entries.append({
                        "path": item_path,
                        "name": name,
                        "type": "directory" if os.path.isdir(item_path) else "file",
                        "size": stat.st_size,
                        "modified": stat.st_mtime
                    })
        else:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                stat = os.stat(item_path)
                entries.append({
                    "path": item_path,
                    "name": item,
                    "type": "directory" if os.path.isdir(item_path) else "file",
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
        
        result = {
            "path": path,
            "count": len(entries),
            "entries": entries
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error listing directory: {str(e)}")]
        )

async def create_directory_tool(arguments: dict) -> CallToolResult:
    """Create a new directory"""
    path = arguments["path"]

    iro = is_read_only()
    if not iro:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Create operations are disabled in read-only mode.")]
        )
    
    if not is_path_allowed(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {path}")]
        )
    
    try:
        os.makedirs(path, exist_ok=True)
        result = {
            "success": True,
            "path": path,
            "message": "Directory created successfully"
        }
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error creating directory: {str(e)}")]
        )

async def delete_file_tool(arguments: dict) -> CallToolResult:
    """Delete a file"""
    path = arguments["path"]

    iro = is_read_only()
    if not iro:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Delete operations are disabled in read-only mode.")]
        )
    
    if not is_path_allowed(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {path}")]
        )
    
    if not os.path.exists(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: File not found: {path}")]
        )
    
    if not os.path.isfile(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Not a file: {path}")]
        )
    
    try:
        os.remove(path)
        result = {
            "success": True,
            "path": path,
            "message": "File deleted successfully"
        }
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error deleting file: {str(e)}")]
        )

async def delete_directory_tool(arguments: dict) -> CallToolResult:
    """Delete a directory"""
    path = arguments["path"]
    recursive = arguments.get("recursive", False)

    iro = is_read_only()
    if not iro:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Delete operations are disabled in read-only mode.")]
        )
    
    if not is_path_allowed(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {path}")]
        )
    
    if not os.path.exists(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Directory not found: {path}")]
        )
    
    if not os.path.isdir(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Not a directory: {path}")]
        )
    
    try:
        if recursive:
            shutil.rmtree(path)
        else:
            os.rmdir(path)
        
        result = {
            "success": True,
            "path": path,
            "message": "Directory deleted successfully"
        }
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error deleting directory: {str(e)}")]
        )

async def move_file_tool(arguments: dict) -> CallToolResult:
    """Move or rename a file or directory"""
    source = arguments["source"]
    destination = arguments["destination"]

    iro = is_read_only()
    if not iro:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Move operations are disabled in read-only mode.")]
        )
    
    if not is_path_allowed(source) or not is_path_allowed(destination):
        return CallToolResult(
            content=[TextContent(type="text", text="Error: Access denied")]
        )
    
    if not os.path.exists(source):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Source not found: {source}")]
        )
    
    try:
        shutil.move(source, destination)
        result = {
            "success": True,
            "source": source,
            "destination": destination,
            "message": "Moved successfully"
        }
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error moving: {str(e)}")]
        )

async def copy_file_tool(arguments: dict) -> CallToolResult:
    """Copy a file or directory"""
    source = arguments["source"]
    destination = arguments["destination"]

    iro = is_read_only()
    if not iro:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Copy operations are disabled in read-only mode.")]
        )
    
    if not is_path_allowed(source) or not is_path_allowed(destination):
        return CallToolResult(
            content=[TextContent(type="text", text="Error: Access denied")]
        )
    
    if not os.path.exists(source):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Source not found: {source}")]
        )
    
    try:
        if os.path.isfile(source):
            shutil.copy2(source, destination)
        else:
            shutil.copytree(source, destination)
        
        result = {
            "success": True,
            "source": source,
            "destination": destination,
            "message": "Copied successfully"
        }
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error copying: {str(e)}")]
        )

async def search_files_tool(arguments: dict) -> CallToolResult:
    """Search for files matching a pattern"""
    directory = arguments["directory"]
    pattern = arguments["pattern"]
    recursive = arguments.get("recursive", True)
    
    if not is_path_allowed(directory):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {directory}")]
        )
    
    if not os.path.exists(directory):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Directory not found: {directory}")]
        )
    
    try:
        path_obj = Path(directory)
        if recursive:
            matches = list(path_obj.rglob(pattern))
        else:
            matches = list(path_obj.glob(pattern))
        
        results = [str(match) for match in matches]
        
        result = {
            "directory": directory,
            "pattern": pattern,
            "count": len(results),
            "matches": results
        }
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error searching: {str(e)}")]
        )

async def get_file_info_tool(arguments: dict) -> CallToolResult:
    """Get detailed information about a file or directory"""
    path = arguments["path"]
    
    if not is_path_allowed(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Access denied to {path}")]
        )
    
    if not os.path.exists(path):
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: Path not found: {path}")]
        )
    
    try:
        stat = os.stat(path)
        abs_path = os.path.abspath(path)
        
        info = {
            "path": abs_path,
            "name": os.path.basename(path),
            "type": "directory" if os.path.isdir(path) else "file",
            "size": stat.st_size,
            "created": stat.st_ctime,
            "modified": stat.st_mtime,
            "accessed": stat.st_atime,
            "permissions": oct(stat.st_mode)[-3:],
        }
        
        if os.path.isfile(path):
            info["extension"] = os.path.splitext(path)[1]
        
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(info, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error getting file info: {str(e)}")]
        )
