from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
import urllib3

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INTENT = (
    "Hey! I need to create a push notification to get eligible users to enroll in the "
    "PayPal Debit Card"
)


def load_dotenv(path: Path = PROJECT_ROOT / ".env") -> None:
    """Load simple KEY=VALUE pairs without adding a runtime dependency."""
    if not path.exists():
        return

    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


load_dotenv()

DYNSEG_BASE_URL = os.getenv(
    "RPS_DYNSEG_BASE_URL",
    "https://msmaster.qa.paypal.com:20068/v1/dynsegmentationserv",
)
REQUEST_TIMEOUT_SECONDS = float(os.getenv("RPS_REQUEST_TIMEOUT_SECONDS", "45"))
COSMOS_LLM_BASE_URL = os.getenv(
    "COSMOS_LLM_BASE_URL",
    "https://aiplatform.dev51.cbf.dev.paypalinc.com/cosmosai/llm/v1",
).rstrip("/")
COSMOS_LLM_MODEL = os.getenv("COSMOS_LLM_MODEL", "gpt-5-mini")
COSMOS_LLM_API_KEY_ENV = "COSMOS_LLM_API_KEY"
COSMOS_LLM_TIMEOUT_SECONDS = float(os.getenv("COSMOS_LLM_TIMEOUT_SECONDS", "45"))
COSMOS_LLM_MAX_TOKENS = int(os.getenv("COSMOS_LLM_MAX_TOKENS", "1200"))

STOPWORDS = {
    "about",
    "audience",
    "audiences",
    "create",
    "customer",
    "customers",
    "for",
    "have",
    "hey",
    "into",
    "need",
    "notification",
    "push",
    "segment",
    "segments",
    "that",
    "the",
    "their",
    "user",
    "users",
    "want",
    "who",
    "with",
}

SYNONYM_RULES = [
    (
        ("paypal one card", "one card", "debit card", "paypal debit card", "ppdc", "cdc"),
        (
            "paypal one card",
            "one card",
            "paypal debit card",
            "consumer debit",
            "consumer_debit",
            "debit",
            "debit card",
            "debit_card",
            "ppdc",
            "cdc",
        ),
    ),
    (
        (
            "not enrolled",
            "not enroll",
            "do not have",
            "does not have",
            "have not",
            "has not",
            "no ",
            "without",
            "unenrolled",
        ),
        (
            "eligible",
            "no",
            "no active",
            "no_debit",
            "non",
            "non_ppdc",
            "nonppdc",
            "not",
            "not enrolled",
            "without",
        ),
    ),
    (("pay later", "bnpl"), ("pay later", "pay_later", "bnpl")),
    (("crypto", "pyusd"), ("crypto", "pyusd")),
    (("passkey", "login"), ("passkey", "login", "authentication")),
]

NEGATIVE_INTENT_PHRASES = (
    "not ",
    "no ",
    "without",
    "do not",
    "does not",
    "have not",
    "has not",
    "not enrolled",
    "not enroll",
    "unenrolled",
)
NEGATIVE_AUDIENCE_PATTERNS = (
    "do not have",
    "does not have",
    "has no",
    "no active",
    "no debit",
    "no_debit",
    "non ppdc",
    "non_ppdc",
    "nonppdc",
    "not enrolled",
    "without",
)
POSITIVE_OWNERSHIP_PATTERNS = (
    "card linked",
    "has accounts with",
    "has paypal issued",
    "has ppdc",
    "product enrolled",
    "user who has",
    "users who has",
    "with debit card",
)


class RpsApiError(RuntimeError):
    """Raised when a read-only RPS request fails."""


class CosmosLlmError(RuntimeError):
    """Raised when copy generation through Cosmos LLM fails."""


@dataclass(frozen=True)
class CopyDraft:
    title: str
    body: str


@dataclass(frozen=True)
class AudienceRecommendation:
    code: str
    segment_id: str
    description: str
    status: str
    audience_count: str
    country: str
    owner: str
    matched_terms: list[str]
    score: int


@dataclass(frozen=True)
class AudienceOption:
    recommendation: AudienceRecommendation
    details: dict[str, Any]


@dataclass(frozen=True)
class DemoResult:
    intent: str
    copy: CopyDraft
    audience: AudienceOption | None
    suggestions: list[AudienceOption]


def normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", str(value).lower())).strip()


def contains_term(text: str, term: str) -> bool:
    normalized_term = normalize(term)
    if not normalized_term:
        return False
    if len(normalized_term) <= 3:
        return f" {normalized_term} " in f" {text} "
    return normalized_term in text


def csv_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    return str(value)


def audience_count(value: Any) -> str:
    if value in (None, ""):
        return "Unavailable"
    if value == -1:
        return "Unavailable (-1 from QA)"
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return str(value)


def has_negative_intent(intent: str) -> bool:
    normalized_intent = f" {intent.lower()} "
    return any(phrase in normalized_intent for phrase in NEGATIVE_INTENT_PHRASES)


def build_search_terms(intent: str) -> list[str]:
    normalized_intent = normalize(intent)
    terms = {
        token for token in normalized_intent.split() if len(token) >= 3 and token not in STOPWORDS
    }

    lower_intent = intent.lower()
    for triggers, synonyms in SYNONYM_RULES:
        if any(trigger in lower_intent for trigger in triggers):
            terms.update(synonyms)

    quoted_phrases = re.findall(r'"([^"]+)"', intent)
    terms.update(phrase for phrase in quoted_phrases if normalize(phrase))

    return sorted(terms)


def score_record(
    record: dict[str, Any],
    terms: list[str],
    intent: str,
) -> tuple[int, list[str]]:
    normalized_code = normalize(record.get("code", ""))
    normalized_description = normalize(record.get("description", ""))
    normalized_extra = normalize(
        " ".join(
            [
                csv_value(record.get("country_codes")),
                csv_value(record.get("regions")),
                str(record.get("created_by", "")),
                csv_value(record.get("co_owners")),
                str(record.get("type", "")),
            ]
        )
    )

    matched_terms = []
    score = 0
    for term in terms:
        matched = False
        if contains_term(normalized_code, term):
            score += 4
            matched = True
        if contains_term(normalized_description, term):
            score += 2
            matched = True
        if contains_term(normalized_extra, term):
            score += 1
            matched = True
        if matched:
            matched_terms.append(term)

    lifecycle_status = str(record.get("lifecycle_status", "")).upper()
    if lifecycle_status == "ACTIVE":
        score += 3

    if has_negative_intent(intent):
        text = normalize(f"{record.get('code', '')} {record.get('description', '')}")
        if any(pattern in text for pattern in NEGATIVE_AUDIENCE_PATTERNS):
            score += 30
        elif "eligible" in text:
            score += 8
        if any(pattern in text for pattern in POSITIVE_OWNERSHIP_PATTERNS):
            score -= 15

    return score, matched_terms


def recommendation_from_record(
    record: dict[str, Any],
    score: int,
    matched_terms: list[str],
) -> AudienceRecommendation:
    return AudienceRecommendation(
        code=str(record.get("code", "")),
        segment_id=str(record.get("id", "")),
        description=str(record.get("description", "")),
        status=str(record.get("lifecycle_status", "")),
        audience_count=audience_count(record.get("audience_count")),
        country=csv_value(record.get("country_codes")) or csv_value(record.get("regions")),
        owner=str(record.get("created_by", "")),
        matched_terms=matched_terms[:8],
        score=score,
    )


def audience_option_from_record(
    record: dict[str, Any],
    score: int = 0,
    matched_terms: list[str] | None = None,
) -> AudienceOption:
    return AudienceOption(
        recommendation=recommendation_from_record(record, score, matched_terms or []),
        details=record,
    )


def rank_dynamic_segment_options(
    dynamic_segments: list[dict[str, Any]],
    intent: str,
    limit: int = 3,
) -> list[AudienceOption]:
    terms = build_search_terms(intent)
    scored: list[tuple[int, list[str], dict[str, Any]]] = []

    for record in dynamic_segments:
        score, matched_terms = score_record(record, terms, intent)
        if score > 0:
            scored.append((score, matched_terms, record))

    if not scored:
        return []

    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        audience_option_from_record(record, score, matched_terms)
        for score, matched_terms, record in scored[:limit]
    ]


def choose_top_dynamic_segment(
    dynamic_segments: list[dict[str, Any]],
    intent: str,
) -> AudienceRecommendation | None:
    ranked = rank_dynamic_segment_options(dynamic_segments, intent, limit=1)
    if not ranked:
        return None
    return ranked[0].recommendation


def request_json(method: str, path: str, **kwargs: Any) -> Any:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url = path if path.startswith("http") else f"{DYNSEG_BASE_URL}{path}"
    try:
        response = requests.request(
            method,
            url,
            timeout=REQUEST_TIMEOUT_SECONDS,
            verify=False,
            **kwargs,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RpsApiError(f"{method} {url} failed: {exc}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise RpsApiError(f"{method} {url} returned non-JSON response") from exc


def fetch_segment_catalog() -> dict[str, Any]:
    return request_json(
        "POST",
        "/segments",
        headers={"Content-Type": "application/json"},
        json={"get_all_segments": True},
    )


def recommend_audience(intent: str) -> AudienceRecommendation | None:
    catalog = fetch_segment_catalog()
    dynamic_segments = catalog.get("dynamic_segments") or []
    return choose_top_dynamic_segment(dynamic_segments, intent)


def recommend_audience_options(intent: str, limit: int = 3) -> list[AudienceOption]:
    catalog = fetch_segment_catalog()
    dynamic_segments = catalog.get("dynamic_segments") or []
    return rank_dynamic_segment_options(dynamic_segments, intent, limit=limit)


def find_dynamic_segment_record(
    dynamic_segments: list[dict[str, Any]],
    segment_id: str,
) -> dict[str, Any] | None:
    normalized_segment_id = segment_id.strip().lower()
    if not normalized_segment_id:
        return None

    for record in dynamic_segments:
        record_id = str(record.get("id", "")).strip().lower()
        record_code = str(record.get("code", "")).strip().lower()
        if normalized_segment_id in {record_id, record_code}:
            return record
    return None


def get_dynamic_segment(segment_id: str) -> AudienceOption | None:
    catalog = fetch_segment_catalog()
    dynamic_segments = catalog.get("dynamic_segments") or []
    record = find_dynamic_segment_record(dynamic_segments, segment_id)
    if record is None:
        return None
    return audience_option_from_record(record)


def cosmos_api_key() -> str:
    load_dotenv()
    return os.getenv(COSMOS_LLM_API_KEY_ENV, "").strip()


def copy_generation_messages(intent: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You generate PayPal customer communication copy for prototypes. "
                "Return only valid JSON with exactly these string fields: title, body. "
                "The copy should be concise, clear, and appropriate for a push notification. "
                "Push notifications do not have a CTA, so do not include a cta field. "
                "Do not include markdown, explanations, or extra keys."
            ),
        },
        {
            "role": "user",
            "content": (
                "Generate one push notification copy option for this PM intent:\n\n"
                f"{intent.strip()}"
            ),
        },
    ]


def copy_variants_messages(
    intent: str,
    control_copy: CopyDraft,
    count: int = 2,
) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You generate PayPal push notification copy variants for A/B testing. "
                "Return only valid JSON with exactly one key: variants. "
                "variants must be an array of objects with exactly these string fields: "
                "title, body. Push notifications do not have a CTA. "
                "Do not include markdown, explanations, or extra keys."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Generate {count} additional push notification copy variants for this PM intent:\n\n"
                f"{intent.strip()}\n\n"
                "The current control copy is:\n"
                f"Title: {control_copy.title}\n"
                f"Body: {control_copy.body}\n\n"
                "Make the variants meaningfully different from the control and from each other. "
                "Only generate title and body copy."
            ),
        },
    ]


def uses_completion_token_limit(model: str) -> bool:
    normalized_model = model.lower()
    return normalized_model.startswith(("gpt-5", "o1", "o3", "o4"))


def copy_generation_payload(intent: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": COSMOS_LLM_MODEL,
        "messages": copy_generation_messages(intent),
        "response_format": {"type": "json_object"},
    }

    if uses_completion_token_limit(COSMOS_LLM_MODEL):
        payload["max_completion_tokens"] = COSMOS_LLM_MAX_TOKENS
    else:
        payload["max_tokens"] = COSMOS_LLM_MAX_TOKENS
        payload["temperature"] = 0.2

    return payload


def copy_variants_payload(
    intent: str,
    control_copy: CopyDraft,
    count: int = 2,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": COSMOS_LLM_MODEL,
        "messages": copy_variants_messages(intent, control_copy, count=count),
        "response_format": {"type": "json_object"},
    }

    if uses_completion_token_limit(COSMOS_LLM_MODEL):
        payload["max_completion_tokens"] = COSMOS_LLM_MAX_TOKENS
    else:
        payload["max_tokens"] = COSMOS_LLM_MAX_TOKENS
        payload["temperature"] = 0.4

    return payload


def set_payload_token_limit(payload: dict[str, Any], token_limit: int) -> dict[str, Any]:
    updated = dict(payload)
    if "max_completion_tokens" in updated:
        updated["max_completion_tokens"] = token_limit
    else:
        updated["max_tokens"] = token_limit
    return updated


def text_from_message_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                value = item.get("text") or item.get("content") or item.get("value")
                if value is not None:
                    text_parts.append(str(value))
        return "".join(text_parts)
    if isinstance(content, dict):
        value = content.get("text") or content.get("content") or content.get("value")
        return str(value) if value is not None else ""
    return "" if content is None else str(content)


def cosmos_response_summary(data: dict[str, Any]) -> str:
    try:
        choice = data["choices"][0]
    except (KeyError, IndexError, TypeError):
        return "no choices returned"

    message = choice.get("message") if isinstance(choice, dict) else None
    message_keys = sorted(message.keys()) if isinstance(message, dict) else []
    summary = {
        "finish_reason": choice.get("finish_reason") if isinstance(choice, dict) else None,
        "message_keys": message_keys,
        "usage": data.get("usage"),
    }
    return json.dumps(summary, ensure_ascii=True)


def extract_copy_content(data: dict[str, Any]) -> str:
    try:
        choice = data["choices"][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise CosmosLlmError("Cosmos LLM response did not include choices.") from exc

    if not isinstance(choice, dict):
        raise CosmosLlmError("Cosmos LLM response choice had an unexpected shape.")

    if "text" in choice:
        return text_from_message_content(choice.get("text"))

    message = choice.get("message")
    if not isinstance(message, dict):
        raise CosmosLlmError("Cosmos LLM response did not include message content.")

    refusal = message.get("refusal")
    if refusal:
        raise CosmosLlmError(f"Cosmos LLM refused to generate copy: {refusal}")

    return text_from_message_content(message.get("content"))


def parse_copy_response(content: str) -> CopyDraft:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        json_start = cleaned.find("{")
        json_end = cleaned.rfind("}")
        if json_start == -1 or json_end <= json_start:
            snippet = cleaned[:200] or "<empty>"
            raise CosmosLlmError(f"Cosmos LLM returned non-JSON copy output: {snippet}") from exc
        try:
            parsed = json.loads(cleaned[json_start : json_end + 1])
        except json.JSONDecodeError as nested_exc:
            snippet = cleaned[:200] or "<empty>"
            raise CosmosLlmError(
                f"Cosmos LLM returned non-JSON copy output: {snippet}"
            ) from nested_exc

    title = str(parsed.get("title", "")).strip()
    body = str(parsed.get("body", "")).strip()
    if not title or not body:
        raise CosmosLlmError("Cosmos LLM response is missing title or body.")

    return CopyDraft(title=title, body=body)


def json_from_llm_content(content: str) -> Any:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        json_start = cleaned.find("{")
        json_end = cleaned.rfind("}")
        if json_start == -1 or json_end <= json_start:
            snippet = cleaned[:200] or "<empty>"
            raise CosmosLlmError(f"Cosmos LLM returned non-JSON copy output: {snippet}") from exc
        try:
            return json.loads(cleaned[json_start : json_end + 1])
        except json.JSONDecodeError as nested_exc:
            snippet = cleaned[:200] or "<empty>"
            raise CosmosLlmError(
                f"Cosmos LLM returned non-JSON copy output: {snippet}"
            ) from nested_exc


def parse_copy_variants_response(content: str, expected_count: int = 2) -> list[CopyDraft]:
    parsed = json_from_llm_content(content)
    variants = parsed.get("variants") if isinstance(parsed, dict) else None
    if not isinstance(variants, list):
        raise CosmosLlmError("Cosmos LLM variants response is missing variants.")

    copy_variants = []
    for item in variants[:expected_count]:
        if not isinstance(item, dict):
            continue
        title = str(item.get("title", "")).strip()
        body = str(item.get("body", "")).strip()
        if title and body:
            copy_variants.append(CopyDraft(title=title, body=body))

    if len(copy_variants) < expected_count:
        raise CosmosLlmError("Cosmos LLM variants response did not include enough variants.")

    return copy_variants


def post_cosmos_chat_completion(payload: dict[str, Any], api_key: str) -> dict[str, Any]:
    try:
        response = requests.post(
            f"{COSMOS_LLM_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=COSMOS_LLM_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.HTTPError as exc:
        detail = response.text.strip()
        message = f"Cosmos LLM request failed: {exc}"
        if detail:
            message = f"{message} - {detail[:500]}"
        raise CosmosLlmError(message) from exc
    except requests.RequestException as exc:
        raise CosmosLlmError(f"Cosmos LLM request failed: {exc}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise CosmosLlmError("Cosmos LLM returned a non-JSON API response.") from exc
    return data


def generate_copy(intent: str) -> CopyDraft:
    api_key = cosmos_api_key()
    if not api_key:
        raise CosmosLlmError(
            f"Missing {COSMOS_LLM_API_KEY_ENV}. Add it to .env and restart the local demo."
        )

    payload = copy_generation_payload(intent)
    data = post_cosmos_chat_completion(payload, api_key)
    content = extract_copy_content(data)
    if not content.strip():
        retry_payload = set_payload_token_limit(payload, max(COSMOS_LLM_MAX_TOKENS * 2, 2400))
        data = post_cosmos_chat_completion(retry_payload, api_key)
        content = extract_copy_content(data)

    if not content.strip():
        raise CosmosLlmError(
            f"Cosmos LLM returned empty copy output: {cosmos_response_summary(data)}"
        )

    return parse_copy_response(content)


def generate_copy_variants(
    intent: str,
    control_copy: CopyDraft,
    count: int = 2,
) -> list[CopyDraft]:
    api_key = cosmos_api_key()
    if not api_key:
        raise CosmosLlmError(
            f"Missing {COSMOS_LLM_API_KEY_ENV}. Add it to .env and restart the local demo."
        )

    payload = copy_variants_payload(intent, control_copy, count=count)
    data = post_cosmos_chat_completion(payload, api_key)
    content = extract_copy_content(data)
    if not content.strip():
        retry_payload = set_payload_token_limit(payload, max(COSMOS_LLM_MAX_TOKENS * 2, 2400))
        data = post_cosmos_chat_completion(retry_payload, api_key)
        content = extract_copy_content(data)

    if not content.strip():
        raise CosmosLlmError(
            f"Cosmos LLM returned empty copy output: {cosmos_response_summary(data)}"
        )

    return parse_copy_variants_response(content, expected_count=count)


def run_demo_flow(intent: str) -> DemoResult:
    cleaned_intent = intent.strip()
    if not cleaned_intent:
        raise ValueError("Enter an intent before generating copy.")

    copy = generate_copy(cleaned_intent)
    audience_options = recommend_audience_options(cleaned_intent, limit=3)
    return DemoResult(
        intent=cleaned_intent,
        copy=copy,
        audience=audience_options[0] if audience_options else None,
        suggestions=audience_options[1:],
    )
