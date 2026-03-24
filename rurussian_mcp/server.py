from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any
import os
import httpx

# Create the MCP Server
mcp = FastMCP(
    "rurussian-mcp",
    dependencies=["mcp>=1.0.0", "httpx", "pydantic"]
)

# API Configuration
API_BASE_URL = os.getenv("RURUSSIAN_API_URL", "https://rurussian.com/api")
DEFAULT_TIMEOUT = 30.0

# Authentication state
current_api_key: Optional[str] = None
current_user_agent: str = "OpenClaw/1.0"

def get_headers() -> Dict[str, str]:
    headers = {
        "User-Agent": current_user_agent,
        "Content-Type": "application/json"
    }
    if current_api_key:
        headers["Authorization"] = f"Bearer {current_api_key}"
    return headers

@mcp.tool()
def authenticate(api_key: str, user_agent: str = "OpenClaw/1.0") -> str:
    """
    Authenticate with the RuRussian API using your API key.
    You must call this before using other tools.
    """
    global current_api_key, current_user_agent
    current_api_key = api_key
    current_user_agent = user_agent
    
    # Optional: We could verify the key with the backend here.
    # For now, we store it and the backend will reject invalid keys on subsequent calls.
    return "Authentication credentials stored successfully. Future requests will use this API key."

def _check_auth() -> Optional[Dict[str, str]]:
    if not current_api_key:
        return {"error": "Authentication required. Please call the 'authenticate' tool first."}
    return None

@mcp.tool()
async def get_word_data(word: str) -> Dict[str, Any]:
    """
    Get detailed dictionary information, declensions, and context for a Russian word.
    """
    auth_err = _check_auth()
    if auth_err: return auth_err
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        try:
            response = await client.get(
                f"{API_BASE_URL}/word/{word}",
                headers=get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Failed to fetch word data: {str(e)}"}

@mcp.tool()
async def get_sentences(word: str, form_word: str = None, form_id: str = None) -> Dict[str, Any]:
    """
    Get example sentences for a specific word and form.
    """
    auth_err = _check_auth()
    if auth_err: return auth_err
        
    params = {"word": word}
    if form_word: params["formWord"] = form_word
    if form_id: params["formId"] = form_id
        
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        try:
            response = await client.get(
                f"{API_BASE_URL}/rusvibe/sentences",
                params=params,
                headers=get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Failed to fetch sentences: {str(e)}"}

@mcp.tool()
async def generate_zakuska(topic: str = "", mode: str = "default") -> Dict[str, Any]:
    """
    Generate a short Russian text (Zakuska) for reading practice.
    """
    auth_err = _check_auth()
    if auth_err: return auth_err
        
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/zakuska/generate",
                json={"topic": topic, "mode": mode},
                headers=get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Failed to generate zakuska: {str(e)}"}

@mcp.tool()
async def analyze_sentence(sentence: str) -> Dict[str, Any]:
    """
    Analyze a Russian sentence to break down grammar and word forms.
    """
    auth_err = _check_auth()
    if auth_err: return auth_err
        
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/analyze_sentence",
                json={"text": sentence},
                headers=get_headers()
            )
            response.raise_for_status()
            
            # The backend returns SSE stream for this endpoint. 
            # We need to collect the stream into a single JSON response or return raw text.
            # In MCP we can just return the full text for now.
            lines = response.text.strip().split("\n")
            result = []
            for line in lines:
                if line.startswith("data: "):
                    data_str = line[6:]
                    if data_str != "[DONE]":
                        result.append(data_str)
            return {"analysis_stream": result}
        except Exception as e:
            return {"error": f"Failed to analyze sentence: {str(e)}"}

@mcp.tool()
async def translate_text(text: str) -> Dict[str, Any]:
    """
    Translate Russian text to English.
    """
    auth_err = _check_auth()
    if auth_err: return auth_err
        
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        try:
            response = await client.post(
                f"{API_BASE_URL}/translate",
                json={"text": text},
                headers=get_headers()
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Failed to translate text: {str(e)}"}

def main():
    """Main entry point for the MCP server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
