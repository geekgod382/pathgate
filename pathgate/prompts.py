from pathgate.config import server
from mcp.types import (TextContent, GetPromptResult, ListPromptsResult, PromptMessage, Prompt)

@server.list_prompts()
async def list_prompts() -> ListPromptsResult:
    """List available prompts"""
    prompts = [
        Prompt(
            name="analyze_directory",
            description="Generate a prompt to analyze a directory structure",
            arguments=[
                {
                    "name": "directory",
                    "description": "Directory path to analyze",
                    "required": True
                }
            ]
        ),
        Prompt(
            name="find_and_read",
            description="Generate a prompt to find and read files matching a pattern",
            arguments=[
                {
                    "name": "directory",
                    "description": "Directory to search in", 
                    "required": True
                },
                {
                    "name": "pattern",
                    "description": "File pattern to search for",
                    "required": True
                }
            ]
        )
    ]
    
    return ListPromptsResult(prompts=prompts)

@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    """Get a prompt"""
    if name == "analyze_directory":
        directory = arguments["directory"]
        content = f"""Please analyze the directory structure at: {directory}

Use the list_directory_tool to explore the directory and provide insights about:
1. Total number of files and directories
2. File types and their distribution
3. Largest files
4. Directory organization
5. Any potential issues or recommendations"""
        
        return GetPromptResult(
            description=f"Analysis prompt for directory: {directory}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=content)
                )
            ]
        )
    
    elif name == "find_and_read":
        directory = arguments["directory"]
        pattern = arguments["pattern"]
        content = f"""Please find and read files in: {directory}
Pattern: {pattern}

1. Use search_files_tool to find matching files
2. Use read_file_tool to read the contents
3. Provide a summary of what you found"""
        
        return GetPromptResult(
            description=f"Find and read prompt for {pattern} in {directory}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=content)
                )
            ]
        )
    
    else:
        raise ValueError(f"Unknown prompt: {name}")
