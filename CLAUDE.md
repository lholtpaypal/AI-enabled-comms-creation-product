# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this repository.

## Commands

```bash
# Setup (Python 3.11-3.14 required)
python3.13 -m venv .venv && source .venv/bin/activate
make install        # pip install -e ".[dev]"

# Run the local demo
make run            # Python localhost server -> http://127.0.0.1:8000

# Test and lint
make test           # pytest (quiet, from tests/)
make lint           # ruff check
make format         # ruff format
make check          # pytest + ruff check + ruff format --check

# Run a single test
python -m pytest tests/test_flow.py::test_parse_copy_response_handles_json -q
```

## Environment

Copy `.env.example` to `.env` and fill in `COSMOS_LLM_API_KEY`. The app calls `load_dotenv()` at module import time so the file is read without the `python-dotenv` package. RPS API calls require VPN/network access to the QA PayPal host (`msmaster.qa.paypal.com`).

## Architecture

The demo is local-only by default. `make run` launches `python -m oslo_comms_studio`, which starts the standard-library HTTP server in `src/oslo_comms_studio/server.py`. The browser calls the local JSON endpoints, and the Python process makes the Cosmos and RPS API calls.

Core workflow logic lives in `src/oslo_comms_studio/app.py`:

1. **Intent capture** - Local browser UI posts the intent to `/api/demo`.
2. **Copy generation** (`generate_copy`) - POSTs to the Cosmos AI Unified LLM API (OpenAI-compatible `/chat/completions`). Returns a `CopyDraft(title, body, cta)` dataclass parsed from JSON.
3. **Audience recommendation** (`recommend_audience` -> `choose_top_dynamic_segment`) - fetches the full RPS dynamic segment catalog via `fetch_segment_catalog`, then scores every segment against search terms extracted from the intent (`build_search_terms`). Scoring weights: code match (+4), description match (+2), metadata match (+1), ACTIVE status (+3). Negative-intent detection (e.g. "not enrolled") boosts negative-audience segments (+30) and penalises positive-ownership segments (-15).

All new integrations should go behind the flow helpers in `src/oslo_comms_studio/app.py`. `RpsApiError` and `CosmosLlmError` are the two domain exceptions; the localhost server catches them and returns user-facing JSON errors.

## Key configuration constants (in `app.py`)

| Name | Default | Override via env var |
|---|---|---|
| `COSMOS_LLM_MODEL` | `gpt-5-mini` | `COSMOS_LLM_MODEL` |
| `COSMOS_LLM_BASE_URL` | Cosmos AI dev endpoint | `COSMOS_LLM_BASE_URL` |
| `DYNSEG_BASE_URL` | RPS QA host | `RPS_DYNSEG_BASE_URL` |
| `REQUEST_TIMEOUT_SECONDS` | `45` | `RPS_REQUEST_TIMEOUT_SECONDS` |

Local server bind settings live in `server.py` and can be overridden with `OSLO_DEMO_HOST` and `OSLO_DEMO_PORT`.

`STOPWORDS` and `SYNONYM_RULES` in `app.py` drive the term-expansion logic for segment matching. Extend these when adding new product areas.

## Linting

ruff is configured in `pyproject.toml`: line length 100, rules `E F I B UP SIM`, E501 ignored. Quote style is double, indent is spaces.
