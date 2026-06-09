---
name: rps-segmentation-explore
description: Explore PayPal RPS QA segmentation APIs in a read-only way. Use when Codex needs to discover, retrieve, filter, or summarize QA dynamic segments, customer lists, profile attributes, attribute metadata, or evaluate whether a provided QA account belongs to one or more RPS audiences.
---

# RPS Segmentation Explore

## Operating Mode

Use this skill as a read-only API exploration agent for RPS QA. Prefer commands that retrieve metadata, catalogs, profile attributes for approved test accounts, and evaluation results. Do not create segments, update attributes, add list members, remove list members, or otherwise mutate QA data unless the user explicitly asks for that specific write operation.

Use `curl -k -sS` for the QA endpoints and pipe to `jq` for compact summaries. If network/DNS fails in the sandbox, rerun the same `curl` command with escalated network approval.

For endpoint details and validated examples, read [api-exploration.md](references/api-exploration.md).

## Workflow

1. Identify the user's target: dynamic segment, customer list, attribute metadata, profile attributes, or membership evaluation.
2. Use the narrowest read endpoint first. Avoid `get_all_segments` unless catalog-wide search is necessary.
3. Save large catalog responses to `/private/tmp` before filtering with `jq` or `rg`.
4. Summarize exact commands run, counts returned, matching IDs/codes, and caveats.
5. Call out when an endpoint exposes metadata only and does not prove full rule logic.

## Core QA Hosts

- Dynamic segmentation service: `https://msmaster.qa.paypal.com:20068/v1/dynsegmentationserv`
- RPS read service: `https://msmaster.qa.paypal.com:14751/rpsreadserv/v1`

## Guardrails

- Treat account numbers and encrypted account numbers as sensitive test data. Only query profile attributes or evaluate membership for account IDs provided or approved by the user.
- For broad catalog searches, return aggregate counts and a small set of relevant matches rather than dumping raw JSON.
- If searching for an attribute in segment definitions, remember the available segment retrieve response may only expose metadata and descriptions, not the full rule tree.
