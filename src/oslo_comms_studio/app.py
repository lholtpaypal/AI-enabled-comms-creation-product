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
RPS_API_CONTEXT_PATH = PROJECT_ROOT / "resources" / "rps-api-context.txt"
RPS_SEARCH_CONTEXT_MAX_CHARS = 5_000
RPS_SEARCH_MAX_REQUESTS = int(os.getenv("RPS_SEARCH_MAX_REQUESTS", "3"))
RPS_RERANK_CANDIDATE_LIMIT = int(os.getenv("RPS_RERANK_CANDIDATE_LIMIT", "25"))

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
RPS_SEARCH_ALLOWED_FILTERS = {"type", "codes", "region", "country", "created_by"}
RPS_SEARCH_ALLOWED_FIELDS = {
    "id",
    "code",
    "description",
    "audience_count",
    "created_by",
    "type",
}
RPS_SEARCH_DEFAULT_FIELDS = (
    "id",
    "code",
    "description",
    "audience_count",
    "created_by",
    "type",
)
RPS_SEARCH_REQUIRED_FIELDS = ("id", "code")


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
class RpsSearchRequest:
    method: str
    endpoint: str
    payload: dict[str, Any]
    reason: str = ""


@dataclass(frozen=True)
class RpsSearchPlan:
    audience_summary: str
    searches: list[RpsSearchRequest]


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


def rps_api_context_excerpt(path: Path = RPS_API_CONTEXT_PATH) -> str:
    fallback = (
        "Use POST /segments/search with Content-Type application/json. "
        "Supported filters include type, codes, region, country, and created_by. "
        "Supported fields include id, code, description, audience_count, created_by, and type."
    )
    if not path.exists():
        return fallback

    text = path.read_text(errors="ignore")
    start = text.find("Segment Filters")
    if start == -1:
        start = text.find("Dynamic Segments")
    if start == -1:
        return text[:RPS_SEARCH_CONTEXT_MAX_CHARS] or fallback

    end = text.find("How to integrate", start)
    if end == -1:
        end = min(len(text), start + RPS_SEARCH_CONTEXT_MAX_CHARS)
    return text[start:end][:RPS_SEARCH_CONTEXT_MAX_CHARS] or fallback


def rps_search_plan_messages(intent: str) -> list[dict[str, str]]:
    return [
        {
            "role": "system",
            "content": (
                "You plan read-only RPS QA Dynamic Segment searches. "
                "Return only valid JSON with exactly these top-level keys: "
                "audience_summary, searches. searches must contain at most three objects. "
                "Each search object must use method POST, endpoint /segments/search, and a payload "
                "for the documented search API. Allowed payload filters are type, codes, region, "
                'country, and created_by. Always set filters.type to ["dynamic_segment"]. '
                "Allowed fields are id, code, description, audience_count, created_by, and type. "
                "Do not use profile APIs, customer-list mutation APIs, evaluate APIs, or "
                "get_all_segments. Favor broad retrieval over exact guessing: use natural business "
                "terms, product names, abbreviations, negated forms, and common code fragments in "
                "filters.codes. It is acceptable for RPS to return hundreds of candidate segments; "
                "the client will rerank candidates after retrieval."
            ),
        },
        {
            "role": "user",
            "content": (
                "RPS API context:\n"
                f"{rps_api_context_excerpt()}\n\n"
                "Submitted PM intent:\n"
                f"{intent.strip()}\n\n"
                "Return JSON in this shape:\n"
                "{"
                '"audience_summary":"short description",'
                '"searches":[{'
                '"reason":"why this search should find reusable audiences",'
                '"method":"POST",'
                '"endpoint":"/segments/search",'
                '"payload":{'
                '"filters":{"type":["dynamic_segment"],"codes":["search term"]},'
                '"fields":["id","code","description","audience_count","created_by","type"],'
                '"sort_by":"code",'
                '"sort_order":"asc"'
                "}"
                "}]"
                "}"
            ),
        },
    ]


def rps_search_plan_payload(intent: str) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": COSMOS_LLM_MODEL,
        "messages": rps_search_plan_messages(intent),
        "response_format": {"type": "json_object"},
    }

    if uses_completion_token_limit(COSMOS_LLM_MODEL):
        payload["max_completion_tokens"] = COSMOS_LLM_MAX_TOKENS
    else:
        payload["max_tokens"] = COSMOS_LLM_MAX_TOKENS
        payload["temperature"] = 0.1

    return payload


def normalize_search_list(value: Any, max_items: int = 12) -> list[str]:
    if isinstance(value, str):
        raw_values = [value]
    elif isinstance(value, list):
        raw_values = value
    else:
        return []

    normalized = []
    seen = set()
    for item in raw_values:
        cleaned = str(item).strip()
        if not cleaned:
            continue
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(cleaned[:100])
        if len(normalized) >= max_items:
            break
    return normalized


def expand_code_filter_values(values: list[str], max_items: int = 18) -> list[str]:
    expanded = []
    seen = set()
    for value in values:
        variants = [value]
        if " " in value:
            variants.extend([value.replace(" ", "_"), value.replace(" ", "")])
        for variant in variants:
            cleaned = variant.strip()
            key = cleaned.lower()
            if not cleaned or key in seen:
                continue
            seen.add(key)
            expanded.append(cleaned)
            if len(expanded) >= max_items:
                return expanded
    return expanded


def sanitize_rps_search_fields(value: Any) -> list[str]:
    requested = normalize_search_list(value, max_items=len(RPS_SEARCH_ALLOWED_FIELDS))
    fields = [field for field in requested if field in RPS_SEARCH_ALLOWED_FIELDS]
    if not fields:
        fields = list(RPS_SEARCH_DEFAULT_FIELDS)

    for required in reversed(RPS_SEARCH_REQUIRED_FIELDS):
        if required in fields:
            fields.remove(required)
        fields.insert(0, required)
    return fields


def sanitize_rps_search_filters(value: Any) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        raise ValueError("RPS search payload must include filters.")

    filters: dict[str, list[str]] = {}
    for key, raw_values in value.items():
        if key not in RPS_SEARCH_ALLOWED_FILTERS:
            continue

        values = normalize_search_list(raw_values)
        if key == "type":
            if not values:
                values = ["dynamic_segment"]
            if {item.lower() for item in values} != {"dynamic_segment"}:
                raise ValueError("RPS search may only target dynamic_segment.")
            filters["type"] = ["dynamic_segment"]
        elif key == "codes":
            expanded_values = expand_code_filter_values(values)
            if expanded_values:
                filters[key] = expanded_values
        elif values:
            filters[key] = values

    filters["type"] = ["dynamic_segment"]
    if not any(key in filters for key in ("codes", "region", "country", "created_by")):
        raise ValueError("RPS search must include at least one targeted filter.")
    return filters


def sanitize_rps_search_payload(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("RPS search payload must be a JSON object.")

    payload: dict[str, Any] = {
        "filters": sanitize_rps_search_filters(value.get("filters")),
        "fields": sanitize_rps_search_fields(value.get("fields")),
    }

    sort_by = str(value.get("sort_by", "")).strip()
    if sort_by in RPS_SEARCH_ALLOWED_FIELDS:
        payload["sort_by"] = sort_by

    sort_order = str(value.get("sort_order", "")).strip().lower()
    if sort_order in {"asc", "desc"}:
        payload["sort_order"] = sort_order

    return payload


def search_payload_signature(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, ensure_ascii=True)


def parse_rps_search_plan(content: str) -> RpsSearchPlan:
    parsed = json_from_llm_content(content)
    if not isinstance(parsed, dict):
        raise CosmosLlmError("Cosmos LLM RPS search plan must be a JSON object.")

    raw_searches = parsed.get("searches")
    if not isinstance(raw_searches, list):
        raise CosmosLlmError("Cosmos LLM RPS search plan is missing searches.")

    searches: list[RpsSearchRequest] = []
    seen_payloads = set()
    for raw_search in raw_searches[:RPS_SEARCH_MAX_REQUESTS]:
        if not isinstance(raw_search, dict):
            continue

        method = str(raw_search.get("method", "POST")).strip().upper()
        endpoint = str(raw_search.get("endpoint", "/segments/search")).strip()
        if method != "POST" or endpoint != "/segments/search":
            continue

        try:
            payload = sanitize_rps_search_payload(raw_search.get("payload"))
        except ValueError:
            continue

        signature = search_payload_signature(payload)
        if signature in seen_payloads:
            continue
        seen_payloads.add(signature)
        searches.append(
            RpsSearchRequest(
                method=method,
                endpoint=endpoint,
                payload=payload,
                reason=str(raw_search.get("reason", "")).strip(),
            )
        )

    if not searches:
        raise CosmosLlmError("Cosmos LLM did not produce a usable RPS search plan.")

    return RpsSearchPlan(
        audience_summary=str(parsed.get("audience_summary", "")).strip(),
        searches=searches,
    )


def fallback_rps_search_plan(intent: str) -> RpsSearchPlan:
    terms = build_search_terms(intent)
    preferred_terms = sorted(
        terms,
        key=lambda term: (
            " " not in term and "_" not in term,
            len(term) < 5,
            len(term),
            term,
        ),
    )

    codes = expand_code_filter_values(preferred_terms, max_items=24)
    searches = []
    for index in range(0, min(len(codes), 24), 8):
        chunk = codes[index : index + 8]
        if not chunk:
            continue
        searches.append(
            RpsSearchRequest(
                method="POST",
                endpoint="/segments/search",
                payload={
                    "filters": {"type": ["dynamic_segment"], "codes": chunk},
                    "fields": list(RPS_SEARCH_DEFAULT_FIELDS),
                    "sort_by": "code",
                    "sort_order": "asc",
                },
                reason="Fallback code-fragment search derived from the submitted intent.",
            )
        )
        if len(searches) >= RPS_SEARCH_MAX_REQUESTS:
            break

    return RpsSearchPlan(
        audience_summary="Fallback RPS dynamic segment search.",
        searches=searches,
    )


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
    return rank_dynamic_segment_records(
        dynamic_segments, intent, limit=limit, require_positive=True
    )


def rank_dynamic_segment_records(
    dynamic_segments: list[dict[str, Any]],
    intent: str,
    limit: int = 3,
    require_positive: bool = False,
) -> list[AudienceOption]:
    terms = build_search_terms(intent)
    scored: list[tuple[int, list[str], dict[str, Any]]] = []

    for record in dynamic_segments:
        score, matched_terms = score_record(record, terms, intent)
        if score > 0 or not require_positive:
            scored.append((score, matched_terms, record))

    if not scored:
        return []

    scored.sort(
        key=lambda item: (
            item[0],
            str(item[2].get("lifecycle_status", "")).upper() == "ACTIVE",
            item[2].get("audience_count") not in (None, "", -1),
        ),
        reverse=True,
    )
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


def search_segments(search: RpsSearchRequest) -> list[dict[str, Any]]:
    data = request_json(
        search.method,
        search.endpoint,
        headers={"Content-Type": "application/json"},
        json=search.payload,
    )
    if not isinstance(data, dict):
        raise RpsApiError(f"{search.method} {search.endpoint} returned an unexpected response.")

    dynamic_segments = data.get("dynamic_segments") or []
    if not isinstance(dynamic_segments, list):
        raise RpsApiError(f"{search.method} {search.endpoint} returned invalid dynamic_segments.")
    return [record for record in dynamic_segments if isinstance(record, dict)]


def fetch_dynamic_segments_by_codes(codes: list[str]) -> list[dict[str, Any]]:
    clean_codes = normalize_search_list(codes, max_items=RPS_RERANK_CANDIDATE_LIMIT)
    if not clean_codes:
        return []

    data = request_json(
        "POST",
        "/segments",
        headers={"Content-Type": "application/json"},
        json={"segment_codes": clean_codes},
    )
    if not isinstance(data, dict):
        raise RpsApiError("POST /segments returned an unexpected response.")

    dynamic_segments = data.get("dynamic_segments") or []
    if not isinstance(dynamic_segments, list):
        raise RpsApiError("POST /segments returned invalid dynamic_segments.")
    return [record for record in dynamic_segments if isinstance(record, dict)]


def generate_rps_search_plan(intent: str) -> RpsSearchPlan:
    api_key = cosmos_api_key()
    if not api_key:
        raise CosmosLlmError(
            f"Missing {COSMOS_LLM_API_KEY_ENV}. Add it to .env and restart the local demo."
        )

    payload = rps_search_plan_payload(intent)
    data = post_cosmos_chat_completion(payload, api_key)
    content = extract_copy_content(data)
    if not content.strip():
        retry_payload = set_payload_token_limit(payload, max(COSMOS_LLM_MAX_TOKENS * 2, 2400))
        data = post_cosmos_chat_completion(retry_payload, api_key)
        content = extract_copy_content(data)

    if not content.strip():
        raise CosmosLlmError(
            f"Cosmos LLM returned empty RPS search plan: {cosmos_response_summary(data)}"
        )
    return parse_rps_search_plan(content)


def dedupe_dynamic_segment_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped = []
    seen = set()
    for record in records:
        key = str(record.get("id") or record.get("code") or "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(record)
    return deduped


def execute_rps_search_plan(plan: RpsSearchPlan) -> list[dict[str, Any]]:
    records = []
    for search in plan.searches:
        records.extend(search_segments(search))
    return dedupe_dynamic_segment_records(records)


def enrich_dynamic_segment_records(
    records: list[dict[str, Any]],
    intent: str,
    max_records: int = RPS_RERANK_CANDIDATE_LIMIT,
) -> list[dict[str, Any]]:
    ranked_options = rank_dynamic_segment_records(
        records,
        intent,
        limit=max_records,
        require_positive=False,
    )
    ranked_records = [option.details for option in ranked_options]
    codes = [option.recommendation.code for option in ranked_options if option.recommendation.code]
    if not codes:
        return ranked_records

    try:
        enriched = fetch_dynamic_segments_by_codes(codes)
    except RpsApiError:
        return ranked_records
    return enriched or ranked_records


def rps_rerank_messages(
    intent: str, options: list[AudienceOption], limit: int
) -> list[dict[str, str]]:
    candidates = [
        {
            "id": option.recommendation.segment_id,
            "code": option.recommendation.code,
            "description": option.recommendation.description,
            "audience_count": option.recommendation.audience_count,
            "created_by": option.recommendation.owner,
            "type": option.details.get("type"),
            "score": option.recommendation.score,
        }
        for option in options[:RPS_RERANK_CANDIDATE_LIMIT]
    ]
    return [
        {
            "role": "system",
            "content": (
                "You choose the best reusable RPS QA Dynamic Segments for a PM intent. "
                "Return only valid JSON with exactly one key: segment_ids. "
                "segment_ids must be an ordered array of candidate ids. "
                "Prefer direct semantic matches, explicit negation/eligibility when requested, "
                "and reusable active dynamic-segment-looking audiences over one-off test lists."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Intent:\n{intent.strip()}\n\n"
                f"Return the best {limit} candidate ids from this JSON candidate list:\n"
                f"{json.dumps(candidates, ensure_ascii=True)}"
            ),
        },
    ]


def rps_rerank_payload(
    intent: str,
    options: list[AudienceOption],
    limit: int = 3,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": COSMOS_LLM_MODEL,
        "messages": rps_rerank_messages(intent, options, limit),
        "response_format": {"type": "json_object"},
    }

    if uses_completion_token_limit(COSMOS_LLM_MODEL):
        payload["max_completion_tokens"] = min(COSMOS_LLM_MAX_TOKENS, 800)
    else:
        payload["max_tokens"] = min(COSMOS_LLM_MAX_TOKENS, 800)
        payload["temperature"] = 0.1

    return payload


def rerank_audience_options_with_llm(
    intent: str,
    options: list[AudienceOption],
    limit: int = 3,
) -> list[AudienceOption]:
    if len(options) <= 1:
        return options[:limit]

    api_key = cosmos_api_key()
    if not api_key:
        return options[:limit]

    payload = rps_rerank_payload(intent, options, limit=limit)
    data = post_cosmos_chat_completion(payload, api_key)
    content = extract_copy_content(data)
    parsed = json_from_llm_content(content)
    if not isinstance(parsed, dict):
        return options[:limit]

    requested_ids = normalize_search_list(parsed.get("segment_ids"), max_items=limit)
    if not requested_ids:
        return options[:limit]

    options_by_id = {
        option.recommendation.segment_id.lower(): option
        for option in options
        if option.recommendation.segment_id
    }
    ranked = []
    seen = set()
    for segment_id in requested_ids:
        key = segment_id.lower()
        option = options_by_id.get(key)
        if option is None or key in seen:
            continue
        seen.add(key)
        ranked.append(option)

    for option in options:
        key = option.recommendation.segment_id.lower()
        if key not in seen:
            ranked.append(option)
        if len(ranked) >= limit:
            break
    return ranked[:limit]


def search_audience_options(intent: str, limit: int = 3) -> list[AudienceOption]:
    records: list[dict[str, Any]] = []
    plan_error: RpsApiError | None = None
    try:
        plan = generate_rps_search_plan(intent)
        records.extend(execute_rps_search_plan(plan))
    except CosmosLlmError:
        pass
    except RpsApiError as exc:
        if not fallback_rps_search_plan(intent).searches:
            raise
        records = []
        plan_error = exc

    broad_plan = fallback_rps_search_plan(intent)
    if broad_plan.searches:
        try:
            records.extend(execute_rps_search_plan(broad_plan))
        except RpsApiError as exc:
            if not records:
                if plan_error is not None:
                    raise plan_error from exc
                raise

    records = dedupe_dynamic_segment_records(records)

    if not records:
        return []

    records = enrich_dynamic_segment_records(records, intent)
    ranked = rank_dynamic_segment_records(
        records,
        intent,
        limit=max(limit, RPS_RERANK_CANDIDATE_LIMIT),
        require_positive=False,
    )
    try:
        return rerank_audience_options_with_llm(intent, ranked, limit=limit)
    except CosmosLlmError:
        return ranked[:limit]


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
    audience_options = search_audience_options(cleaned_intent, limit=3)
    return DemoResult(
        intent=cleaned_intent,
        copy=copy,
        audience=audience_options[0] if audience_options else None,
        suggestions=audience_options[1:],
    )
