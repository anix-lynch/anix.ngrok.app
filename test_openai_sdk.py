import os
import json
import requests
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
MCP_SERVER_URL = "https://anix.ngrok.app/mcp"  # Or http://localhost:8000/mcp
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("⚠️  Please set OPENAI_API_KEY in .env or environment")
    exit(1)

client = OpenAI(api_key=OPENAI_API_KEY)

# 1. Define the tools for OpenAI (Client-side definition)
# Note: In a real MCP client, you'd fetch these from the server via tools/list
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_resume_info",
            "description": "Get Anix Lynch's complete resume including skills, projects, and experience",
            "parameters": {
                "type": "object",
                "properties": {},
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_skills",
            "description": "Get Anix's technical skills",
            "parameters": {
                "type": "object",
                "properties": {
                    "min_weight": {"type": "integer", "description": "Minimum skill weight (1-10)"}
                },
            },
        },
    }
]

def call_mcp_tool(tool_name, arguments):
    """Execute the tool call against the MCP server"""
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    try:
        response = requests.post(MCP_SERVER_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        
        if "error" in data:
            return f"Error: {data['error']['message']}"
        
        # Extract the content from the MCP response
        # Result format: {"content": [{"type": "text", "text": "..."}]}
        content = data["result"]["content"][0]["text"]
        return content
        
    except Exception as e:
        return f"Failed to call MCP: {str(e)}"

def main():
    print(f"🤖 Connecting to OpenAI with MCP Tool Calling...")
    print(f"🔌 MCP Server: {MCP_SERVER_URL}")
    
    # User query
    user_query = "What are Anix's top skills and has he worked with AI agents?"
    print(f"\n❓ User: {user_query}")
    
    messages = [{"role": "user", "content": user_query}]
    
    # 1. First call to OpenAI to decide which tool to use
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    if tool_calls:
        print(f"🛠️  OpenAI decided to call {len(tool_calls)} tool(s)")
        
        # Extend conversation with assistant's reply
        messages.append(response_message)
        
        # 2. Execute tool calls
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)
            
            print(f"   → Calling {function_name}({function_args})...")
            
            # Call our MCP server
            function_response = call_mcp_tool(function_name, function_args)
            
            print(f"   ← Got response ({len(function_response)} chars)")
            
            # Add tool response to conversation
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
            
        # 3. Second call to OpenAI to generate final answer
        print("📝 Generating final answer...")
        final_response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
        )
        
        print(f"\n🤖 Assistant: {final_response.choices[0].message.content}")
        
    else:
        print("OpenAI didn't want to call any tools.")

if __name__ == "__main__":
    main()
