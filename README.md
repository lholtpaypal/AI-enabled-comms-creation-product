# Oslo Comms Studio

Localhost demo for the first slice of an AI-native communications creation workflow.

The app now runs from your laptop only. There is no Streamlit app and no public-facing UI. Your browser loads a local page from a Python server, and that same Python server makes the Cosmos LLM and RPS API calls from your machine.

## How It Works Now

You do **not** need separate frontend and backend servers.

```text
Your browser
  -> http://127.0.0.1:8000
  -> local Python server
  -> Cosmos LLM API
  -> RPS QA API
```

The local Python server does two jobs:

1. Serves the browser page you will share in the meeting.
2. Handles JSON API requests from that page and calls Cosmos/RPS.

The browser never calls Cosmos or RPS directly.

## Project Layout

```text
src/oslo_comms_studio/app.py      # Workflow, LLM, and RPS recommendation helpers
src/oslo_comms_studio/server.py   # Localhost browser demo and JSON endpoints
src/oslo_comms_studio/__main__.py # Lets `python -m oslo_comms_studio` run the demo
tests/                            # Unit tests for flow helpers
.env.example                      # Local environment variable template
ai-native-comms-creation.md       # Product/workflow source narrative
prototype.jsx                     # Visual/storyboard source prototype
message_config.json               # PIE-like config example
message_text.json                 # PIE-like message example
```

## Setup

Use Python 3.11-3.14.

From the project root:

```bash
python3 -m venv .venv
make install
```

If you prefer activating the virtual environment first, this also works:

```bash
python3 -m venv .venv
source .venv/bin/activate
make install
```

`make install` installs the package locally plus the dev tools used for tests and linting.

## Configure API Access

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
COSMOS_LLM_API_KEY=your_key_here
COSMOS_LLM_MODEL=gpt-5-mini
```

The real `.env` file is ignored so local credentials do not get committed.

RPS access also requires VPN/network access to the QA host:

```text
https://msmaster.qa.paypal.com:20068/v1/dynsegmentationserv
```

## Run The Demo

Start the local server:

```bash
make run
```

You should see something like:

```text
Local demo running at http://127.0.0.1:8000
Press Ctrl+C to stop.
```

Open that URL in your browser:

```text
http://127.0.0.1:8000
```

Leave this terminal running while you use the browser demo. Stop it with `Ctrl+C`.

If port `8000` is busy, the server automatically tries the next available port up to `8020`. You can also choose a port:

```bash
OSLO_DEMO_PORT=8010 make run
```

## Do I Need Two Terminal Shells?

Usually, no.

For the meeting demo, you need:

1. One terminal running `make run`.
2. One browser tab open to the printed localhost URL.

A second terminal is optional. It is useful only if you want to run test commands or call the local API with `curl` while the server is still running.

## Browser Demo Flow

1. Open `http://127.0.0.1:8000`.
2. Confirm the top-right status says local config is ready.
3. Enter the PM intent.
4. Click **Generate workflow**.
5. The page calls the local server at `POST /api/demo`.
6. The local server calls Cosmos to generate copy.
7. The local server calls RPS to rank Dynamic Segments.
8. The page displays the generated copy in two editable fields: Title and Body.
9. The phone preview on the right updates live from the Title and Body fields.
10. The page displays the selected RPS Segment ID and all returned RPS segment details.
11. The page displays the next two suggested Dynamic Segments beside the RPS section.
12. The page asks whether to create content variations for A/B testing.
13. If you click **Yes**, Cosmos generates two additional Title/Body variants.
14. The bottom of the page shows three standalone push notification mockups in one row: the current control copy plus the two generated variants.

After the first workflow run:

- Click **Regenerate copy text** to call Cosmos again using the same declared intent.
- Edit the generated Title or Body directly; the phone notification preview updates as you type.
- Paste a different Dynamic Segment ID into the RPS Segment ID box to refresh the details.
- Click either suggested audience card to use that segment instead.
- Click **Yes** in Section 5 to generate A/B testing variants for copy only.

## Local API

The browser calls these local endpoints:

```text
GET  /api/health
POST /api/demo
POST /api/copy
POST /api/segment
POST /api/variants
```

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

Manual demo request:

```bash
curl -X POST http://127.0.0.1:8000/api/demo \
  -H "Content-Type: application/json" \
  -d '{"intent":"Create a push notification for users not enrolled in PayPal One Card"}'
```

`POST /api/demo` returns generated copy, the recommended RPS Dynamic Segment, and two suggested Dynamic Segment alternatives.

Regenerate copy only:

```bash
curl -X POST http://127.0.0.1:8000/api/copy \
  -H "Content-Type: application/json" \
  -d '{"intent":"Create a push notification for users not enrolled in PayPal One Card"}'
```

Look up a pasted Dynamic Segment ID:

```bash
curl -X POST http://127.0.0.1:8000/api/segment \
  -H "Content-Type: application/json" \
  -d '{"segment_id":"DS-7637634650901768635"}'
```

Generate two additional A/B copy variants:

```bash
curl -X POST http://127.0.0.1:8000/api/variants \
  -H "Content-Type: application/json" \
  -d '{"intent":"Create a push notification for PayPal Debit Card enrollment","title":"You are eligible for the PayPal Debit Card","body":"Use your PayPal balance anywhere and earn cash back on everyday purchases."}'
```

`POST /api/demo` returns:

- `copy`: generated push notification copy
- `selected_audience`: the top RPS Dynamic Segment
- `suggested_audiences`: the next two Dynamic Segment options

`POST /api/variants` returns:

- `variants`: two generated push notification copy variants with `title` and `body` only

## Test And Verify

Run the automated checks:

```bash
make check
```

That runs:

```text
pytest
ruff check
ruff format --check
```

Useful individual commands:

```bash
make test       # unit tests only
make lint       # lint only
make format     # auto-format code
```

The automated tests do not need the local server to be running. They test the Python workflow helpers directly.

For a full manual smoke test:

1. Start the server with `make run`.
2. Open the browser URL and run the demo once.
3. Optional: in a second terminal, call `/api/health` or `/api/demo` with `curl`.

## Troubleshooting

If the browser says the Cosmos key is missing, check `.env` and restart `make run`.

If Cosmos fails, confirm `COSMOS_LLM_API_KEY`, `COSMOS_LLM_MODEL`, and VPN/internal network access.

If Cosmos returns empty copy output, restart the server and make sure `.env` has:

```bash
COSMOS_LLM_MAX_TOKENS=1200
```

If you still see the old empty-output error after restarting, check that your browser is not pointed at a stale server on another port:

```bash
lsof -nP -iTCP:8000-8020 -sTCP:LISTEN
curl http://127.0.0.1:8000/api/health
```

The health response from the fixed server should include:

```json
{"server_version":"push-enrollment-paypal-logo-v5","max_tokens":1200}
```

If RPS fails, confirm VPN/network access to the QA host.

If `.venv/bin/python` is missing or broken, recreate the virtual environment:

```bash
python3 -m venv .venv
make install
```

## Integration Notes

Current flow:

1. User enters intent in the local browser UI.
2. Local server generates draft copy through the shared Cosmos AI OpenAI-compatible chat completions endpoint.
3. Browser renders the copy in editable Title and Body fields and mirrors them in the phone preview.
4. Local server searches RPS dynamic segments and returns the top match plus two suggested alternatives.
5. User can paste a Dynamic Segment ID, and the local server refreshes details from RPS.

Keep future integrations behind the flow helpers in `src/oslo_comms_studio/app.py`.
