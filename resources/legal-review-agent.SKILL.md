---
name: Legal Review Agent
description: Prepare and submit a PayPal notification legal ticket in Quickbase — validate prerequisites, compute the legal response date, and draft the Overview field and asset PDF.
---

# Legal Review Agent

## Overview
This skill walks a PayPal team through submitting a **legal ticket for a notification** in
Quickbase, end to end: checking prerequisites, filling each field correctly, computing the legal
response date, drafting the Overview text, and assembling the asset PDF. Notification copy must
be **legally approved** before it ships.

**Quickbase app:** https://pypl.quickbase.com/nav/app/bmgg9ch4m/action/appoverview

> This skill prepares and guides the legal submission. It does not write the marketing copy
> (see `content-writer-agent`) or pull the population count itself (see `rps-search-agent`).

## When to use
- A user is ready to send a notification's copy to legal for review.
- A user needs help filling the Quickbase request, computing the response date, or writing the
  Overview.
- A user is resubmitting after legal feedback (revised asset).

## Before you start — prerequisites
1. **Notification copy ready as a PDF.**
2. **Population count** pulled from the RPS portal (by segment ID — use `rps-search-agent`).

**Source:** "How to Submit a Legal Ticket for Notifications."

## Step-by-step submission
1. Go to the Quickbase app (link above) → click **New Request**.
2. Enter a **6-digit Kanban code** for tracking. This is freeform / up to the submitter
   (e.g., a date, batch number, or sprint reference).
3. Select **region and country** (e.g., North America, United States).
4. Create a **submission name** — clear and descriptive, identifying the notification and batch
   (e.g., "Oslo Commerce Reengagement — BNPL Discovery — Batch 1").
5. **Submission Type** — select the primary product for the message (e.g., Pay Later, Debit
   Card, Rewards).
6. Select the **channel** (e.g., Push Notification).
7. Select the **frequency** (e.g., 2x monthly).
8. Set **Target Audience** to **Consumer**.
9. Add the **population count** (from the RPS portal, by segment ID).
10. Select the **target launch date**.
11. Set the **legal response date** — must be **at least 3 business days after the submission
    date**. **Do not count weekends or PayPal holidays.**
12. Fill the **Overview** field — describe who you are targeting and the intent: include the
    **segment**, the **behavior trigger**, and the **value proposition**.
13. Click the **Assets** tab → **Add Asset**. The asset must be a **PDF** containing the full
    notification copy, **send logic**, and **suppression rules**.
14. Set **Asset Type**: **Initial Asset** for a first submission, **Revised Asset** for a
    resubmission after legal feedback.
15. Click **Save and Close**, then **Save and Close** again on the confirmation screen.
16. Click the new **Send** button to move the ticket into the active review queue.
    **The ticket is not submitted to legal until this Send step is complete.**

**Source:** "How to Submit a Legal Ticket for Notifications."

## Computing the legal response date (helper)
- Start from the **submission date**.
- Count **3 business days** forward.
- **Skip Saturdays, Sundays, and PayPal holidays.**
- The response date must be **on or after** that third business day.

When a user gives a submission date, walk the calendar day by day and state the earliest valid
response date. If you are unsure which days are PayPal holidays, say so and ask the user to
confirm rather than guessing.

## Overview field — drafting template
Help the user write a tight Overview using this pattern (from the example in the source doc):

> "Targeting **[segment]** who **[behavior trigger / current state]**. Message **[value
> proposition / what it offers]** at **[moment / context]**."

Example: "Targeting Casual Buyers who are pre-approved for Pay Later but have never used it.
Message introduces 0% APR split payments at a moment of high purchase intent."

## Asset PDF checklist
The uploaded PDF must include:
- [ ] Full notification copy (all channels/locales as applicable)
- [ ] Send logic
- [ ] Suppression rules

## Common pitfalls
- Forgetting the final **Send** click — the ticket sits as a draft and legal never sees it.
- Response date set fewer than 3 business days out, or counting weekends/holidays.
- Using **Initial Asset** on a resubmission (should be **Revised Asset**).

## What not to do
- Don't invent the Quickbase field options, holiday calendars, or approval SLAs beyond the
  documented "3 business days."
- Don't confirm legal approval status — this skill prepares the submission; legal owns the decision.

---
**🆘 Need help?** → **#help-communication** on Slack
