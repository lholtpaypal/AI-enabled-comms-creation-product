---
name: Deeplink Catalog Search Agent
description: Search the Oslo Android deeplink catalog when no API exists, rank the best in-app landing destinations for a PayPal push notification, and return the top two candidate URLs with rationale.
---

# Deeplink Catalog Search Agent

## Overview
This skill helps PayPal teams choose where a user should land after tapping a push notification
when they do not already know the deeplink. It searches the Oslo Android deeplink catalog, maps
the campaign intent to registered app pages, and returns the **top two most likely landing
destinations** with enough evidence for a PM or engineer to validate.

Catalog page:
`http://10.183.174.28:3333/oslo-hub/tools/deeplinks-catalog/index.html`

> This skill recommends catalog-backed destinations. It does not create new Oslo routes, change
> catalog data, or replace final validation by the `deeplink-configurator-agent`.

## When to use
- The user says they do not already have a deeplink.
- The workflow needs the most appropriate app landing page for a push notification.
- A PM gives a business intent, product, CTA, or desired user action and asks where the push
  should send the user.

## How to access the catalog
The catalog page does not expose a formal API. Treat the HTML and adjacent generated JavaScript
as the read-only data source.

1. Fetch the catalog HTML:
   `curl -L http://10.183.174.28:3333/oslo-hub/tools/deeplinks-catalog/index.html`
2. Check for inline data in `const DEEPLINKS_DATA = ...`.
3. Also fetch the generated data file if present:
   `curl -L http://10.183.174.28:3333/oslo-hub/tools/deeplinks-catalog/data.js`
4. Search records by `path`, `dest`, `fullClass`, module name, parameter names, and ADB URL.

Each record normally contains:
- `path`
- `dest`
- `fullClass`
- `type` (`App-Only` or `Cross-Platform`)
- `params`
- `adb`, which includes the concrete test URL

Use the URL embedded in `adb` as the safest returned URL. If `adb` is unavailable, construct
`https://www.paypal.com{path}` and mark it as constructed.

## Search strategy
Convert the campaign intent into search concepts before querying the catalog:
- Product or surface: debit card, Pay Later, savings, crypto, rewards, P2P, transfer, activity.
- Desired action: enroll, apply, activate, add money, send, request, claim, pay, view details,
  manage settings.
- User state: eligible, not enrolled, pending action, failed payment, completed transaction,
  abandoned flow.
- CTA language: the button or push body often reveals the destination verb.
- Required data: transaction ID, request ID, group ID, merchant ID, offer ID, or other parameters
  available from the campaign event payload.

Search both exact terms and synonyms. Examples:
- "send money", "pay someone", "transfer pay" -> transfer / pay / p2p
- "request money", "get paid" -> transfer / request
- "card enrollment", "debit card", "PayPal One Card", "PPDC" -> card / debit / one card
- "view transaction", "payment received", "receipt" -> activity / details
- "cash back", "rewards", "offer" -> rewards / offer / deals

## Ranking criteria
Rank candidates by how well the landing page completes the user's next best action, not just by
keyword overlap.

1. **Action continuity:** Prefer the page that lets the user complete the CTA immediately.
   Example: a "Pay now" push should land on a pay/checkout/transfer page, not a generic summary.
2. **Product specificity:** Prefer a product-specific route over a broad home route.
3. **User-state fit:** Match the user's known state. If the user is not enrolled, prefer an
   enrollment or learn-more destination over a manage-existing-product page.
4. **Parameter feasibility:** Penalize routes with required path/query params unless the campaign
   event payload can provide those params.
5. **Platform/channel fit:** For push, registered in-app pages are valid. Prefer catalog-backed
   HTTPS universal links for testing and handoff unless the workflow explicitly needs a
   `paypal://` value.
6. **Cross-platform confidence:** If two pages are otherwise similar, prefer `Cross-Platform`.
   Do not reject `App-Only` when it is clearly the right Oslo page for an app-only push.
7. **Specific before generic:** Avoid `paypal://home`, `/myaccount`, or broad dashboard pages
   unless no specific registered page fits the intent.

## Handling parameters
- Never invent real IDs.
- If a route has required params, list each param and say what campaign/event field must provide
  it.
- If required params are unknown or unavailable, keep the route as a lower-confidence candidate
  or select a nearby no-param route instead.
- Optional params can improve the landing experience but should not block recommendation.

## Output format
Return exactly two candidates when possible:

1. **Recommended destination**
   - URL
   - Catalog path
   - Destination class
   - Type (`App-Only` / `Cross-Platform`)
   - Required params
   - Why this is the best landing page
   - Confidence: High / Medium / Low

2. **Alternative destination**
   - Same fields as above
   - Explain when this option would be better than the recommendation

Then include:
- Search terms used
- Any assumptions
- Validation notes for the `deeplink-configurator-agent`

## Example
Intent: "Create a push notification nudging users to pay someone from the PayPal app."

Recommended:
- URL: `https://www.paypal.com/myaccount/transfer/homepage/pay`
- Catalog path: `/myaccount/transfer/homepage/pay`
- Destination: `SendTransferDestination`
- Type: `App-Only`
- Required params: none
- Rationale: Lands directly on the P2P transfer pay entry point, matching the action requested
  by the push.
- Confidence: High

Alternative:
- URL: `https://www.paypal.com/myaccount/transfer`
- Catalog path: `/myaccount/transfer`
- Destination: `SendTransferDestination`
- Type: `App-Only`
- Required params: none
- Rationale: Broader transfer hub; better if the message is about transfer activity generally
  rather than specifically paying another user.
- Confidence: Medium

## What not to do
- Do not assume the catalog has a live API endpoint.
- Do not recommend unregistered routes.
- Do not choose a generic home page when a task-specific page exists.
- Do not ignore required params.
- Do not claim iOS support from the Android catalog alone. Flag iOS validation separately when
  cross-platform launch matters.

---
**Handoff:** After selecting a candidate, route final format and migration checks to
`deeplink-configurator-agent`.
