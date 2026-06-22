# Push Notification Demo Workflow

**Layout:** Vertical, revealed step by step.

## 1. Campaign Context

The first screen shows only the campaign context question. The user enters a plain-English request, for example:

> "I want to encourage eligible US customers to use PayPal's Buy Now, Pay Later for the first time."

The context is shared with each agent, but no downstream agent runs automatically.

## 2. Copy And Variants

The first action is **Generate copy**, which calls the content writer and returns push notification `title` and `body` only.

Content writer requirements:

- Run a PayPal.com value-prop web-search pass before drafting copy.
- Use the latest usable PayPal.com product-page context as the source of truth.
- Do not treat PayPal products generically when a specific product value prop is available.
- For PayPal Debit Card, use the 5% cash back value prop when relevant.
- For Pay Later / BNPL, use eligible-purchase payment splitting at checkout when relevant.

The generated `title` and `body` are editable. The lock-screen preview updates as the user edits either field.

Variants belong in this same copy step:

- The user can click **Yes** to create two A/B copy variants.
- Variants are generated from the current editable title/body plus the original context.
- Variants only change `title` and `body`.
- The row shows the control copy plus Variant A and Variant B as standalone push notifications.

The user can skip variants and continue to audience.

## 3. Audience And Deeplink

The user clicks **Find RPS segment** only when ready. The RPS Search agent returns one selected Dynamic Segment for the demo UI.

Visible audience output:

- Editable RPS Segment ID.
- RPS details from the selected segment.

Alternative audience cards are intentionally hidden for the demo.

The user then chooses a deeplink:

- Paste an existing deeplink, or
- Click **Find deeplink** to search the Oslo deeplink catalog.

The deeplink search returns the top two registered destinations, and the first one populates the editable deeplink field.

## 4. Upload JSON

The final action is **Build upload JSON**.

For the demo, this is intentionally fakeable:

- Read `resources/reference_campaign.json`.
- Keep the campaign, target audience, QA test-account segment, channel rules, owners, and other settings hard-coded.
- Replace only:
  - `content_payload.localizable_content.en-US.title`
  - `content_payload.localizable_content.en-US.body`
  - `content_payload.non_localizable_content.deep_link`

The resulting JSON can be copied or downloaded for PStudio upload.
