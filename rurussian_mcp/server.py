from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any, Iterable, Tuple
import os
import httpx

mcp = FastMCP(
    "rurussian-mcp",
    dependencies=["mcp>=1.0.0", "httpx", "pydantic"]
)

API_BASE_URL = os.getenv("RURUSSIAN_API_URL", "https://rurussian.com/api").rstrip("/")
DEFAULT_TIMEOUT = 30.0
BUY_SESSION_ENDPOINTS = tuple(
    endpoint.strip()
    for endpoint in os.getenv(
        "RURUSSIAN_BUY_SESSION_ENDPOINTS",
        "/create-checkout-session,/checkout/session,/billing/checkout-session",
    ).split(",")
    if endpoint.strip()
)
CONFIRM_PURCHASE_ENDPOINTS = tuple(
    endpoint.strip()
    for endpoint in os.getenv(
        "RURUSSIAN_CONFIRM_PURCHASE_ENDPOINTS",
        "/verify-checkout-session,/checkout/verify,/payment/verify,/payment/complete",
    ).split(",")
    if endpoint.strip()
)

current_api_key: Optional[str] = os.getenv("RURUSSIAN_API_KEY")
current_user_agent: str = "OpenClaw/1.0"

def _redact(value: Optional[str], visible: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= visible * 2:
        return "*" * len(value)
    return f"{value[:visible]}{'*' * (len(value) - visible * 2)}{value[-visible:]}"

def get_headers(include_auth: bool = True) -> Dict[str, str]:
    headers = {
        "User-Agent": current_user_agent,
        "Content-Type": "application/json"
    }
    if include_auth and current_api_key:
        headers["Authorization"] = f"Bearer {current_api_key}"
    return headers

def _safe_json(response: httpx.Response) -> Dict[str, Any]:
    try:
        data = response.json()
        if isinstance(data, dict):
            return data
        return {"data": data}
    except Exception:
        return {"text": response.text}

def _normalize_endpoint(endpoint: str) -> str:
    endpoint = endpoint.strip()
    if endpoint.startswith("http://") or endpoint.startswith("https://"):
        return endpoint
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    return f"{API_BASE_URL}{endpoint}"

def _extract_first_present(data: Dict[str, Any], keys: Iterable[str]) -> Optional[str]:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return None

async def _try_endpoints(
    method: str,
    endpoint_candidates: Tuple[str, ...],
    payload: Optional[Dict[str, Any]] = None,
    include_auth: bool = False,
) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        for endpoint in endpoint_candidates:
            url = _normalize_endpoint(endpoint)
            try:
                if method == "GET":
                    response = await client.get(url, params=payload, headers=get_headers(include_auth=include_auth))
                else:
                    response = await client.post(url, json=payload or {}, headers=get_headers(include_auth=include_auth))
                if response.status_code < 400:
                    return _safe_json(response), None
                body = _safe_json(response)
                error_message = _extract_first_present(body, ("error", "message", "detail"))
                if error_message:
                    if response.status_code in (401, 403):
                        return None, error_message
                    continue
            except Exception:
                continue
    return None, "No compatible backend purchase endpoint responded successfully."

@mcp.tool()
def authenticate(api_key: str, user_agent: str = "OpenClaw/1.0") -> str:
    """
    Authenticate with the RuRussian API using your API key.
    You must call this before using other tools.
    """
    global current_api_key, current_user_agent
    current_api_key = api_key
    current_user_agent = user_agent
    return "Authentication credentials stored successfully. Future requests will use this API key."

@mcp.tool()
def authentication_status() -> Dict[str, Any]:
    return {
        "authenticated": bool(current_api_key),
        "api_key_preview": _redact(current_api_key),
        "user_agent": current_user_agent
    }

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
            response = await client.get(f"{API_BASE_URL}/word/{word}", headers=get_headers())
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
            response = await client.get(f"{API_BASE_URL}/rusvibe/sentences", params=params, headers=get_headers())
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
            response = await client.post(f"{API_BASE_URL}/zakuska/generate", json={"topic": topic, "mode": mode}, headers=get_headers())
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
            response = await client.post(f"{API_BASE_URL}/analyze_sentence", json={"text": sentence}, headers=get_headers())
            response.raise_for_status()
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
            response = await client.post(f"{API_BASE_URL}/translate", json={"text": text}, headers=get_headers())
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": f"Failed to translate text: {str(e)}"}

@mcp.tool()
async def create_key_purchase_session(
    email: str,
    plan: str,
    success_url: str = "",
    cancel_url: str = "",
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"email": email, "plan": plan}
    if success_url:
        payload["success_url"] = success_url
    if cancel_url:
        payload["cancel_url"] = cancel_url
    response, error = await _try_endpoints("POST", BUY_SESSION_ENDPOINTS, payload=payload, include_auth=False)
    if error:
        return {"error": f"Failed to create purchase session: {error}"}
    checkout_url = _extract_first_present(response or {}, ("url", "checkout_url", "checkoutUrl", "session_url"))
    session_id = _extract_first_present(response or {}, ("session_id", "sessionId", "id"))
    if not checkout_url:
        return {
            "error": "Purchase session created but checkout URL was not found in response.",
            "payment_status": _extract_first_present(response or {}, ("status", "payment_status", "result")) or "unknown",
        }
    return {
        "checkout_url": checkout_url,
        "session_id": session_id,
        "plan": plan,
        "next_step": "Open checkout_url and complete payment, then call confirm_key_purchase with session_id."
    }

@mcp.tool()
async def confirm_key_purchase(
    session_id: str,
    auto_authenticate: bool = True,
    return_api_key: bool = False,
) -> Dict[str, Any]:
    payload = {"session_id": session_id}
    response, error = await _try_endpoints("POST", CONFIRM_PURCHASE_ENDPOINTS, payload=payload, include_auth=False)
    if error:
        response, error = await _try_endpoints("GET", CONFIRM_PURCHASE_ENDPOINTS, payload=payload, include_auth=False)
        if error:
            return {"error": f"Failed to confirm purchase: {error}"}
    status_value = _extract_first_present(response or {}, ("status", "payment_status", "result"))
    api_key = _extract_first_present(response or {}, ("api_key", "apiKey", "key"))
    if not api_key:
        return {
            "confirmed": status_value in {"paid", "success", "completed"},
            "payment_status": status_value or "unknown",
            "message": _extract_first_present(response or {}, ("message", "detail")) or "Payment confirmation returned no API key yet.",
        }
    global current_api_key
    if auto_authenticate:
        current_api_key = api_key
    result: Dict[str, Any] = {
        "confirmed": True,
        "payment_status": status_value or "paid",
        "api_key_preview": _redact(api_key),
        "authenticated_for_session": auto_authenticate
    }
    if return_api_key:
        result["api_key"] = api_key
    return result

def main():
    """Main entry point for the MCP server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
