from __future__ import annotations

from urllib.parse import urlparse

import requests


DEFAULT_BASE_URL = "http://localhost:11434"
CLOUD_MODEL_MARKERS = (":cloud", "-cloud")
DIRECT_CONNECTION_PROXIES = {"http": None, "https": None, "all": None}
SYNTHETIC_TEST_WORKFLOW = (
    "Synthetic local-only test: an internal support team asks AI to draft a customer response "
    "from anonymized ticket notes. A human reviewer must approve the message before sending. "
    "No production system or real personal data is included."
)


def _is_localhost(base_url: str) -> bool:
    parsed = urlparse(base_url)
    return parsed.scheme in {"http", "https"} and parsed.hostname in {"localhost", "127.0.0.1", "::1"}


def is_cloud_or_proxy_model(model_name: str, model_payload: dict[str, object] | None = None) -> bool:
    normalized = model_name.casefold().strip()
    if any(marker in normalized for marker in CLOUD_MODEL_MARKERS):
        return True
    if not model_payload:
        return False
    return bool(model_payload.get("remote_host") or model_payload.get("remote_model"))


def check_ollama_status(base_url: str = DEFAULT_BASE_URL, timeout: float = 1.5) -> dict[str, object]:
    if not _is_localhost(base_url):
        return {
            "available": False,
            "models": [],
            "cloud_models": [],
            "all_models": [],
            "message": "Localhost endpoint required.",
        }

    try:
        response = requests.get(
            f"{base_url.rstrip('/')}/api/tags",
            timeout=timeout,
            allow_redirects=False,
            proxies=DIRECT_CONNECTION_PROXIES,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.RequestException as exc:
        return {
            "available": False,
            "models": [],
            "cloud_models": [],
            "all_models": [],
            "message": f"Local model service unavailable: {exc}",
        }
    except ValueError:
        return {
            "available": False,
            "models": [],
            "cloud_models": [],
            "all_models": [],
            "message": "Local model service returned invalid JSON.",
        }

    local_models: list[str] = []
    cloud_models: list[str] = []
    all_models: list[str] = []
    for item in payload.get("models", []):
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        all_models.append(name)
        if is_cloud_or_proxy_model(name, item):
            cloud_models.append(name)
        else:
            local_models.append(name)

    return {
        "available": True,
        "models": local_models,
        "cloud_models": cloud_models,
        "all_models": all_models,
        "message": "Local model service available.",
    }


def build_enrichment_prompt(workflow_text: str, analysis: dict[str, object], language_name: str) -> str:
    risk = analysis.get("risk", {})
    risk_dict = risk if isinstance(risk, dict) else {}
    return f"""Write a concise executive narrative in {language_name} for a local AI workflow risk audit.
Do not change the score, risk level, detected risks, data categories, or human checkpoints.
Keep it advisory, defensive, and non-operational.
State clearly that the deterministic score remains authoritative for this app.

Risk score: {risk_dict.get("score")}
Risk level: {risk_dict.get("level")}
Workflow type: {analysis.get("workflow_type")}
Workflow text:
{workflow_text[:2500]}
"""


def build_synthetic_test_prompt(language_name: str) -> str:
    return f"""Write a short local-only diagnostic response in {language_name}.
Explain that this is a synthetic Ollama test, not a real workflow audit.
Do not claim compliance certification, remediation, or score validation.

Synthetic workflow:
{SYNTHETIC_TEST_WORKFLOW}
"""


def generate_local_prompt_response(
    prompt: str,
    model: str = "llama3",
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 20.0,
) -> str | None:
    if not _is_localhost(base_url):
        return None
    if is_cloud_or_proxy_model(model):
        return None

    status = check_ollama_status(base_url=base_url)
    local_models = {str(name) for name in status.get("models", [])}
    if not status.get("available") or model not in local_models:
        return None

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }

    try:
        response = requests.post(
            f"{base_url.rstrip('/')}/api/generate",
            json=payload,
            timeout=timeout,
            allow_redirects=False,
            proxies=DIRECT_CONNECTION_PROXIES,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        return None
    except ValueError:
        return None

    text = str(data.get("response", "")).strip()
    return text or None


def generate_enrichment(
    workflow_text: str,
    analysis: dict[str, object],
    language_name: str,
    model: str = "llama3",
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = 20.0,
) -> str | None:
    if not _is_localhost(base_url):
        return None
    if is_cloud_or_proxy_model(model):
        return None

    status = check_ollama_status(base_url=base_url)
    local_models = {str(name) for name in status.get("models", [])}
    if not status.get("available") or model not in local_models:
        return None

    risk = analysis.get("risk", {})
    if not isinstance(risk, dict):
        return None

    prompt = build_enrichment_prompt(workflow_text, analysis, language_name)
    return generate_local_prompt_response(prompt, model=model, base_url=base_url, timeout=timeout)
