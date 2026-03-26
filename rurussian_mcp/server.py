from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any, Iterable, Tuple
import os
import httpx
from urllib.parse import urlparse, parse_qs

mcp = FastMCP(
    "rurussian-mcp",
    dependencies=["mcp>=1.0.0", "httpx", "pydantic"]
)

API_BASE_URL = os.getenv("RURUSSIAN_API_URL", "https://rurussian.com/api").rstrip("/")
DEFAULT_TIMEOUT = 30.0
PAYMENT_SUCCESS_STATUSES = {"paid", "success", "completed"}
PLAN_CATALOG: Dict[str, Dict[str, Any]] = {
    "month_1": {
        "price_usd": 3.75,
        "duration_days": 30,
        "display_name": "1 Month Subscription",
        "marketing_copy": "Fastest way to try RuRussian inside an OpenClaw bot.",
    },
    "year_1": {
        "price_usd": 7.49,
        "duration_days": 365,
        "display_name": "1 Year Subscription",
        "marketing_copy": "Best balance for active Russian-learning bots.",
    },
    "year_3": {
        "price_usd": 21.74,
        "duration_days": 365 * 3,
        "display_name": "3 Years Subscription",
        "marketing_copy": "Lowest long-term cost for always-on tutoring bots.",
    },
}
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
        "/payment/complete,/verify-checkout-session,/checkout/verify,/payment/verify",
    ).split(",")
    if endpoint.strip()
)

current_api_key: Optional[str] = os.getenv("RURUSSIAN_API_KEY")
current_user_agent: str = "OpenClaw/1.0"
current_paid_access: bool = False
current_purchase_context: Dict[str, Any] = {
    "email": "",
    "plan": "",
    "checkout_url": "",
    "session_id": "",
    "payment_status": "",
}

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

def _has_access() -> bool:
    return bool(current_api_key or current_paid_access)

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

def _normalize_status(status_value: Optional[str]) -> str:
    return (status_value or "").strip().lower()

def _is_payment_confirmed(status_value: Optional[str]) -> bool:
    return _normalize_status(status_value) in PAYMENT_SUCCESS_STATUSES

def _extract_session_id_from_url(url: str) -> str:
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        values = parse_qs(parsed.query).get("session_id", [])
        return values[0] if values else ""
    except Exception:
        return ""

def _set_purchase_context(**kwargs: Any) -> None:
    current_purchase_context.update({key: value for key, value in kwargs.items() if value is not None})

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
    global current_api_key, current_user_agent, current_paid_access
    current_api_key = api_key
    current_user_agent = user_agent
    current_paid_access = False
    return "Authentication credentials stored successfully. Future requests will use this API key."

@mcp.tool()
def authentication_status() -> Dict[str, Any]:
    return {
        "authenticated": _has_access(),
        "authentication_method": "api_key" if current_api_key else "paid_checkout" if current_paid_access else "none",
        "api_key_preview": _redact(current_api_key),
        "user_agent": current_user_agent,
        "purchase_context": {
            "email": current_purchase_context.get("email", ""),
            "plan": current_purchase_context.get("plan", ""),
            "session_id": current_purchase_context.get("session_id", ""),
            "payment_status": current_purchase_context.get("payment_status", ""),
            "checkout_url": current_purchase_context.get("checkout_url", ""),
        },
    }

def _check_auth() -> Optional[Dict[str, str]]:
    if not _has_access():
        return {"error": "Authentication required. Call 'authenticate' with an API key or complete the purchase flow first."}
    return None

@mcp.tool()
def list_pricing_plans() -> Dict[str, Any]:
    return {
        "currency": "USD",
        "plans": [
            {
                "plan": plan_id,
                "display_name": plan_data["display_name"],
                "price_usd": plan_data["price_usd"],
                "duration_days": plan_data["duration_days"],
                "marketing_copy": plan_data["marketing_copy"],
            }
            for plan_id, plan_data in PLAN_CATALOG.items()
        ],
        "recommended_bot_flow": [
            "Choose a plan.",
            "Call create_key_purchase_session with the bot-controlled payer email.",
            "Open the checkout_url in a payment-capable browser flow.",
            "After checkout redirects back with session_id, call confirm_key_purchase.",
        ],
    }

@mcp.tool()
def purchase_status() -> Dict[str, Any]:
    return {
        "checkout_started": bool(current_purchase_context.get("checkout_url")),
        "session_id": current_purchase_context.get("session_id", ""),
        "payment_status": current_purchase_context.get("payment_status", ""),
        "paid_access_active": current_paid_access,
        "plan": current_purchase_context.get("plan", ""),
        "email": current_purchase_context.get("email", ""),
    }

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
    if plan not in PLAN_CATALOG:
        return {
            "error": f"Unsupported plan '{plan}'.",
            "available_plans": list(PLAN_CATALOG.keys()),
        }
    payload: Dict[str, Any] = {"email": email, "plan": plan}
    if success_url:
        payload["success_url"] = success_url
    if cancel_url:
        payload["cancel_url"] = cancel_url
    response, error = await _try_endpoints("POST", BUY_SESSION_ENDPOINTS, payload=payload, include_auth=False)
    if error:
        return {"error": f"Failed to create purchase session. {error}"}
    checkout_url = _extract_first_present(response or {}, ("url", "checkout_url", "checkoutUrl", "session_url"))
    session_id = _extract_first_present(response or {}, ("session_id", "sessionId", "id")) or _extract_session_id_from_url(checkout_url or "")
    if not checkout_url:
        return {
            "error": "Purchase session created but checkout URL was not found in response.",
            "payment_status": _extract_first_present(response or {}, ("status", "payment_status", "result")) or "unknown",
        }
    _set_purchase_context(
        email=email,
        plan=plan,
        checkout_url=checkout_url,
        session_id=session_id,
        payment_status="checkout_created",
    )
    return {
        "checkout_url": checkout_url,
        "session_id": session_id,
        "plan": plan,
        "plan_details": PLAN_CATALOG[plan],
        "next_step": "Open checkout_url and complete payment. If the backend does not return session_id immediately, read session_id from the success redirect URL and pass it to confirm_key_purchase.",
        "bot_payment_ready": True,
    }

@mcp.tool()
async def confirm_key_purchase(
    session_id: str,
    auto_authenticate: bool = True,
) -> Dict[str, Any]:
    global current_api_key, current_paid_access
    payload = {"session_id": session_id, "include_api_key": True}
    response, error = await _try_endpoints("POST", CONFIRM_PURCHASE_ENDPOINTS, payload=payload, include_auth=False)
    if error:
        response, error = await _try_endpoints("GET", CONFIRM_PURCHASE_ENDPOINTS, payload=payload, include_auth=False)
        if error:
            return {"error": f"Failed to confirm purchase. {error}"}
            
    status_value = _extract_first_present(response or {}, ("status", "payment_status", "result"))
    api_key = _extract_first_present(response or {}, ("api_key", "apiKey", "key", "token"))
    confirmed = bool(api_key) or _is_payment_confirmed(status_value)
    _set_purchase_context(
        session_id=session_id,
        payment_status=status_value or "unknown",
    )

    if not api_key:
        if confirmed and auto_authenticate:
            current_paid_access = True
        return {
            "confirmed": confirmed,
            "payment_status": status_value or "unknown",
            "authenticated_for_session": bool(confirmed and auto_authenticate),
            "auth_mode": "paid_checkout" if confirmed and auto_authenticate else "none",
            "message": "Payment confirmation processed. No raw API key was returned by the backend, so this MCP session uses checkout-backed access for subsequent calls.",
        }
        
    if auto_authenticate:
        current_api_key = api_key
        current_paid_access = False
        
    return {
        "confirmed": True,
        "payment_status": status_value or "paid",
        "api_key_preview": _redact(api_key),
        "authenticated_for_session": auto_authenticate,
        "auth_mode": "api_key" if auto_authenticate else "none",
    }

def main():
    """Main entry point for the MCP server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
