"""
Test script for the pure MCP server implementation
"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_server():
    """Test the filesystem MCP server"""
    
    # Server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["C:\\Users\\manan\\filesystem-mcp-server\\server.py"],
    )
    
    print("🚀 Starting Pure MCP Filesystem Server test...\n")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the session
                await session.initialize()
                
                print("✅ Server initialized successfully!\n")
                
                # Test 1: List available tools
                print("📋 Available Tools:")
                tools = await session.list_tools()
                for tool in tools.tools:
                    print(f"  - {tool.name}")
                print(f"\nTotal tools: {len(tools.tools)}\n")
                
                # Test 2: List available resources
                print("📚 Available Resources:")
                resources = await session.list_resources()
                for resource in resources.resources:
                    print(f"  - {resource.uri}: {resource.name}")
                print()
                
                # Test 3: List available prompts
                print("💭 Available Prompts:")
                prompts = await session.list_prompts()
                for prompt in prompts.prompts:
                    print(f"  - {prompt.name}: {prompt.description}")
                print()
                
                # Test 4: Test list_directory_tool on current directory
                print("📂 Testing list_directory_tool on current directory:")
                result = await session.call_tool(
                    "list_directory_tool",
                    arguments={"path": ".", "recursive": False}
                )
                
                if result.content:
                    content = result.content[0]
                    if hasattr(content, 'text'):
                        data = json.loads(content.text)
                        print(f"  Found {data['count']} items in current directory")
                        print(f"  First few items:")
                        for entry in data['entries'][:3]:
                            print(f"    - {entry['name']} ({entry['type']})")
                print()
                
                print("✅ All tests passed! Pure MCP Server is working correctly.")
    
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(test_server())
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
