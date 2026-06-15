---
name: Deeplink Configurator Agent
description: Build and validate Oslo deeplinks for PayPal notifications — pick universal-link vs paypal:// by channel, write oslo_deeplink eval expressions, and migrate Venice links to Oslo.
---

# Deeplink Configurator Agent

## Overview
This skill helps PayPal teams pick the **correct deeplink format** for a notification, build the
**`oslo_deeplink`** value (including eval expressions), confirm the destination page is
**registered in Oslo**, and migrate **Venice → Oslo** deeplinks. It is part of Step 1
("Define the experience — where to land the user") and Step 3 ("Configure and validate").

> Keeping users in the in-app ecosystem is the goal: land them on an app page or a PayPal App
> webview.

## When to use
- A user needs a deeplink for a Push, NC alert, email/SMS, paid placement, or NBA tile.
- A user is migrating a Venice deeplink to Oslo.
- A deeplink isn't resolving, loops, or behaves differently on iOS vs Android.

## Rule 1 — Pick format by channel
| Use case | Format | Notes |
|---|---|---|
| **External assets** (email, SMS, paid placements) | `https://www.paypal.com/mobile-app/*` | `paypal://` does **NOT** work for Oslo external messages. |
| **Internal app assets** (push, NC, in-app links) | `paypal://*` (works if page is registered) | `https://www.paypal.com/mobile-app/*` also works for both testing and push. |
| **Testing** | `https://www.paypal.com/mobile-app/*` | `paypal://` testing via ADB can throw `ActivityNotFoundException`. |

Universal links (`https://www.paypal.com/mobile-app/*`) work for **both** Venice and Oslo, so
they can be updated pre-launch. `paypal://` in push is supported mainly for **backward
compatibility with Venice** and is not recommended for new deeplinks.

**Source:** CommsHub FAQ §2 and §11 (Oslo Deeplinks).

## Rule 2 — Use the Oslo field, not the Venice fields
| Field | App | Purpose |
|---|---|---|
| `oslo_deeplink` | Oslo | Navigation destination — **this is the field to populate for Oslo**. |
| `NN_ANDROID` / `NN_IOS` | Venice | Schema + host |
| `nn_payload` | Venice | Query parameters (ignored by Oslo) |

During transition, keep both `nn_payload` (Venice) and `oslo_deeplink` (Oslo) populated; each app
ignores the other's field.

**Source:** CommsHub FAQ §2.1, §9.

## Rule 3 — Universal-link format & eval expressions
**Format:** `https://www.paypal.com/mobile-app/{page-name}`

**Dynamic values** use eval expressions: `${event_code.parameter_name}`

Correct example:
```
https://www.paypal.com/myaccount/activities/details/${p2p_money_received.Transaction_ID}
```
If the payload shows the raw expression instead of a resolved URL, the parameter is likely **not
defined in the event's outcome parameters** in PStudio, or the expression syntax is wrong.

**Source:** CommsHub FAQ §2.2, §2.4, §3.4.

## Rule 4 — Versioning
- **All deeplinks should be on V2. V1 is deprecated.**

**Source:** "Notification gap fill" doc.

## Rule 5 — Confirm the page is registered in Oslo
A deeplink only works if the destination page is registered in Oslo (mobile engineers own
registration).
- **Android:** Oslo Android Deeplinks Catalog —
  https://paypal.atlassian.net/wiki/spaces/Oslo/pages/2820007690
- **iOS:** Apple App Site Association —
  https://www.paypal.com/.well-known/apple-app-site-association

**iOS vs Android parameters can differ** (e.g., iOS `activityItemId` vs Android `transactionId`)
— check both catalogs and confirm required params per platform.

**Source:** CommsHub FAQ §11.2, §11.5.

## QA vs Production gotcha
`oslo_deeplinks` were **backfilled in Production only, not Stage/QA**. Clicks tested in QA may
not navigate. Workaround: manually copy the Production `oslo_deeplink` into the Stage interaction,
or smoke-test in Production.

**Source:** CommsHub FAQ §2.3, §11.6.

## Venice → Oslo migration
| Scenario | Action |
|---|---|
| Venice & Oslo page name + required fields are the **same** | No change — existing deeplink works. |
| Page name or required fields **changed** in Oslo | Update `oslo_deeplink` in PStudio with the new Oslo link. |

Migration steps: confirm the page is registered → update external `paypal://` links to
`https://www.paypal.com/mobile-app/` → populate `oslo_deeplink` for push/NC → test in QA, then prod.

**Source:** CommsHub FAQ §11.5; External Deeplink Migration RFC.

## Tools & references
- **Deeplink Converter for Oslo** —
  https://paypal.atlassian.net/wiki/spaces/CEPl/pages/2825631175/Deeplink+Converter+for+Oslo
- **Configuring deeplinks for Mobile Notification Center Alert** —
  https://paypal.atlassian.net/wiki/spaces/DigitalWallet/pages/2600149335
- **Oslo Comms Deeplink Update Guide** —
  https://paypal.atlassian.net/wiki/spaces/CEPl/pages/2821460227

## Troubleshooting quick hits
- **`Failed to resolve malformed deeplink path`** → page not registered in Oslo; check catalogs.
- **Infinite loop with `paypal://open_web`** → URL-encoding/param issue; use the HTTPS format and
  test with minimal params first. (`paypal://open_web` is live on iOS; Android in progress.)
- **Works in background but goes Home when app is killed** → known Oslo cold-start issue.
- **Works on one platform only** → different param names per platform; escalate to #oslo-deeplinks.

## What not to do
- Don't hand-write a `paypal://` link for an **external** (email/SMS/paid) Oslo message.
- Don't assume a page is registered — verify against the catalog/AASA.
- Don't invent parameter names; confirm them per platform.

---
**🆘 Need help?** → **#help-communication** · **Deeplinks** → **#oslo-deeplinks**
