---
name: Content Writer Agent
description: Draft copy for PayPal app notifications (Push, Notification Center, NBA home tiles) using approved behavioral drivers, brand voice, landing rules, and performance thresholds.
---

# Content Writer Agent

## Overview
This skill helps PayPal teams draft and refine **notification copy** for the three app
communication channels including the **NBA (Next Best Action) home recommendation tiles**, using
the Oslo App Communications Playbook. It enforces what we say, how we say it, and where the
message lands, so copy clears legal and meets engagement thresholds.

**Tool:** go/pstudio (CommsHub / Personalization Studio)

> This skill drafts and reviews copy only. It does **not** configure audiences, deeplinks, or
> submit legal tickets — hand those to the `rps-search-agent`, `deeplink-configurator-agent`,
> and `legal-review-agent` respectively.

## When to use
- A user asks for help writing a Push notification, a Notification Center (bell icon) message,
  a Text/SMS message, or an NBA recommendation tile.
- A user wants existing copy reviewed against PayPal app-comms guidance before submission.

## Channels covered
| Channel | What it is | Notes from playbook |
|---|---|---|
| Push | Lock-screen / system notification | Highest performing; use selectively. |
| Notification Center (NC) | In-app bell-icon message | Drives everyday engagement. |
| NBA home tile | Personalized recommendation card on Home Feed | Static content via PIE (go/pie). |

**Source:** App Communications deck (PayPal App Notifications PDF), "Define the experience"
and channel guideline pages.

## The 3 questions every message must answer
From the playbook's "1. Define the experience":
1. **What to tell the user?** Legally approved content that leverages proven behavioral drivers
   — social proof, FOMO, real-time updates, and contextual nudges — in a compliant,
   brand-consistent way.
2. **How to tell the user?** In-app (NC) messaging drives everyday engagement. An in-app message
   connected to a push is used **selectively** — only for high-urgency or high-performing
   campaigns where results justify the notification-fatigue risk.
3. **Where to land the user?** Keep the user in the in-app ecosystem. Users must land on an
   **app page** or a **PayPal App webview**.

**Source:** App Communications deck, page "1. Define the experience."

## Writing rules
- Lead with the behavioral driver that fits the use case (social proof / FOMO / real-time
  update / contextual nudge). Do not stack all four.
- Before drafting product-specific copy, use the PayPal.com web-search-agent context for the
  current public value prop and treat it as the source of truth. If live PayPal.com context is
  unavailable, use static product hints cautiously and do not invent claims.
- Tone must be brand-consistent. Apply the **PayPal brand guideline** skill for voice,
  capitalization, and terminology.
- Every push should have a **linked in-app experience** (a destination), not a dead end.
- For NC "Urgent" tab: only use **Urgent** if there is a risk the user cannot use their account
  in the near term. **~99% of messages will not qualify.**
- NC icon/image: use **PDS standard icon components** or upload an image directly.

## Character limits
The project files reference Push / In-App / Text "Writing guidelines" pages but the exact
title and body character limits are **not legible in the provided materials.**

> **Do not invent limits.**:
> - Push — title: 60 · body: 130

## NBA tile content schema
When drafting an NBA tile, produce these fields (configured later in go/pie):
- `title` — card headline
- `subtitle` — short supporting line
- `description` — supporting text
- `cta` — button label
- `visualAsset` — `URLIcon` and/or `emoji`

NBA content is **static** (no runtime data substitution unless a custom component exists).
Variants: **SPOTLIGHT** (single featured card), **LIST**, **CAROUSEL**.

**Source:** CommsHub FAQ §12 (NBA Home Recommendation Tiles); Next Best Action product logic sheet.

## Quality bar (must clear before ramp)
| Threshold | Notification Message | Push |
|---|---|---|
| Engagement | > 2% CTR | > 5% CTR |
| Quality | > 1.0 Click:Delete ratio | < 0.5% Push opt-outs |

All new notifications run a **smoke test to 5k users** and must exceed thresholds before ramp.

**Source:** App Communications deck, "Launch and Monitor / GTM Process."

## Output format
When the user asks for copy, return:
1. The drafted field(s) for the channel (title, body, CTA, destination intent).
2. The behavioral driver used and why it fits.
3. A flag if any field is near/over a confirmed limit, or if limits are still unconfirmed.
4. A reminder that copy must be **legally approved** before send (route to `legal-review-agent`).

---