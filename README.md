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

Copy generation also runs a live PayPal.com value-prop search before calling Cosmos. By default it
uses DuckDuckGo's HTML endpoint to find public `paypal.com` product pages, fetches the top pages,
and passes short source highlights into the content-writer prompt. If that search path is
unavailable, the demo falls back to the static product hints in code. Set
`PAYPAL_VALUE_PROP_SEARCH_ENABLED=false` in `.env` to disable live search for local testing.

RPS access also requires VPN/network access to the QA host:

```text
https://msmaster.qa.paypal.com:20068/v1/dynsegmentationserv
```

Deeplink search reads the Oslo catalog page and generated `data.js` directly because the catalog
does not expose an API:

```text
http://10.183.174.28:3333/oslo-hub/tools/deeplinks-catalog/index.html
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
3. Enter the PM campaign context. The first screen intentionally shows only this question.
4. Click **Generate copy**.
5. The page calls the local server at `POST /api/copy`.
6. The local server runs the PayPal.com value-prop web-search pass, then calls Cosmos to generate copy from the intent plus the latest usable PayPal.com context.
7. The page displays the generated copy in two editable fields: Title and Body.
8. The phone preview on the right updates live from the Title and Body fields.
9. Decide whether to add A/B copy variants. If you click **Yes**, Cosmos generates two additional Title/Body variants from the current editable copy.
10. Continue to audience, then click **Find RPS segment** when you want the RPS Search agent to run.
11. The page calls `POST /api/audience`, then displays one selected RPS Segment ID and RPS details. Alternative audiences are not shown in the demo UI.
12. Paste your own deeplink or click **Find deeplink** when you want the Deeplink Catalog Search agent to run.
13. The page calls `POST /api/deeplinks`, then displays the selected deeplink URL and two catalog-backed destination cards.
14. Click **Build upload JSON** to create a PStudio upload package from `resources/reference_campaign.json`.
15. The JSON package keeps the reference campaign hard-coded and replaces only the push title, body, and deeplink.

After copy generation:

- Click **Regenerate copy text** to call Cosmos again using the same declared intent.
- Edit the generated Title or Body directly; the phone notification preview updates as you type.
- Click **Yes** in the copy step to generate A/B testing variants for copy only, or continue without variants.
- Click **Find RPS segment** to search RPS when you are ready.
- Paste a different Dynamic Segment ID into the RPS Segment ID box to refresh the details.
- Paste your own deeplink, or click **Find deeplink** to refresh the top two deeplink candidates from the current intent and copy.
- Click **Build upload JSON** after copy and deeplink are set.

## Local API

The browser calls these local endpoints:

```text
GET  /api/health
POST /api/copy
POST /api/audience
POST /api/segment
POST /api/deeplinks
POST /api/variants
POST /api/package
```

Health check:

```bash
curl http://127.0.0.1:8000/api/health
```

Generate or regenerate copy only:

```bash
curl -X POST http://127.0.0.1:8000/api/copy \
  -H "Content-Type: application/json" \
  -d '{"intent":"Create a push notification for users not enrolled in PayPal One Card"}'
```

Find RPS audience candidates:

```bash
curl -X POST http://127.0.0.1:8000/api/audience \
  -H "Content-Type: application/json" \
  -d '{"intent":"Create a push notification for users not enrolled in PayPal One Card"}'
```

Look up a pasted Dynamic Segment ID:

```bash
curl -X POST http://127.0.0.1:8000/api/segment \
  -H "Content-Type: application/json" \
  -d '{"segment_id":"DS-7637634650901768635"}'
```

Refresh deeplink candidates only:

```bash
curl -X POST http://127.0.0.1:8000/api/deeplinks \
  -H "Content-Type: application/json" \
  -d '{"intent":"Create a push notification nudging users to pay someone from the PayPal app","title":"Pay someone in seconds","body":"Send money from your PayPal app."}'
```

Generate two additional A/B copy variants:

```bash
curl -X POST http://127.0.0.1:8000/api/variants \
  -H "Content-Type: application/json" \
  -d '{"intent":"Create a push notification for PayPal Debit Card enrollment","title":"You are eligible for the PayPal Debit Card","body":"Use your PayPal balance anywhere and earn cash back on everyday purchases."}'
```

Build a demo upload package from the hard-coded reference campaign:

```bash
curl -X POST http://127.0.0.1:8000/api/package \
  -H "Content-Type: application/json" \
  -d '{"title":"Pay later today","body":"Split eligible purchases at checkout.","deeplink":"https://www.paypal.com/myaccount/paylater"}'
```

`POST /api/audience` returns:

- `selected_audience`: the top RPS Dynamic Segment
- `suggested_audiences`: additional Dynamic Segment options for API consumers; the demo UI hides them

`POST /api/variants` returns:

- `variants`: two generated push notification copy variants with `title` and `body` only

`POST /api/deeplinks` returns:

- `selected_deeplink`: the top Oslo catalog destination
- `suggested_deeplinks`: the alternate destination
- `deeplink_options`: both returned deeplink candidates

`POST /api/package` returns:

- `package`: the reference campaign JSON with only `title`, `body`, and `deep_link` replaced
- `updated_fields`: the three fields inserted into the hard-coded package

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
2. Open the browser URL and generate copy once.
3. Generate or skip variants, then click **Find RPS segment** and **Find deeplink** to run those agents separately.
4. Click **Build upload JSON** and confirm the package contains the current title, body, and deeplink.
5. Optional: in a second terminal, call `/api/health`, `/api/copy`, `/api/audience`, `/api/deeplinks`, or `/api/package` with `curl`.

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
{"server_version":"transcript-demo-v15","max_tokens":1200}
```

If RPS fails, confirm VPN/network access to the QA host.

If deeplink search fails, confirm VPN/network access to the Oslo hub catalog host and verify the
`DEEPLINK_CATALOG_URL` / `DEEPLINK_CATALOG_DATA_URL` values in `.env`.

If `.venv/bin/python` is missing or broken, recreate the virtual environment:

```bash
python3 -m venv .venv
make install
```

## Integration Notes

Current flow:

1. User enters campaign context in the local browser UI.
2. Local server generates draft copy through the shared Cosmos AI OpenAI-compatible chat completions endpoint.
3. Browser renders the copy in editable Title and Body fields, mirrors them in the phone preview, and can generate two copy variants.
4. User clicks **Find RPS segment**; the local server searches RPS dynamic segments and returns the top match.
5. User can paste a Dynamic Segment ID, and the local server refreshes details from RPS.
6. User clicks **Find deeplink**; the local server searches the Oslo catalog and returns the top two registered app destinations.
7. User clicks **Build upload JSON**; the local server reads `resources/reference_campaign.json` and replaces only the push title, body, and deeplink.

Keep future integrations behind the flow helpers in `src/oslo_comms_studio/app.py`.
