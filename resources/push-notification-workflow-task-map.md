# Push Notification Campaign Package — Task Map

Columns: the **task**, the **context needed to complete it** (tools, prompts, resources — left blank where the context is user-supplied and not something I can specify), and **who completes the task** (user or model).

> Legal review is split into two tasks: a **model pre-screen** (automated triage) and a **final review** owned by the user.

| # | Task | Context needed to complete task (tools / prompts / resources) | Who completes task |
|---|------|----------------------------------------------------------------|--------------------|
| 1 | **Declared Intent** — user states the campaign goal in the intent box, kicking off the flow. | — | **User** |
| 2 | **Generate Copy** — model generates the push copy once from the declared intent and displays it in an editable box. | **Tool:** `content-writer-agent` (LLM completion)<br>**Prompt:** system prompt for persuasive, marketer-grade copy + few-shot title/body examples<br>**Resources:** push-notification character limits, brand/tone guidelines | **Model** |
| 3 | **Audience (RPS Search Agent)** — forms the RPS API call, shows the terms it chose, returns Segment ID + Details. | **Tool:** RPS Search API (segment query + lookup-by-ID)<br>**Prompt:** translate intent (e.g., "eligible for PayPal Debit Card") into RPS query terms<br>**Resources:** RPS segment schema, eligibility-criteria taxonomy, product → eligibility-attribute mapping | **Model** |
| 4 | **Suggested Audience Options** — surfaces 2 ranked alternative segments; selection updates the audience boxes. | **Tool:** RPS Search API (candidate/alternative segments)<br>**Prompt:** produce ranked alternatives relevant to the intent<br>**Resources:** catalog of available segments + relevance ranking; current intent + selected segment | **Model** |
| 5 | **A/B Content Variants** — generates 2 extra Title/Body variants and renders 3 notification mock-ups. | **Tool:** `content-writer-agent`<br>**Prompt:** generate diverse variants; **constraint:** vary Title + Body only<br>**Resources:** original declared intent, output schema `{title, body}`, diversity instruction | **Model** |
| 6 | **Deeplink Search** — finds the in-app destination the notification should open and attaches it. | **Tool:** deeplink registry/catalog search API + resolver/validator<br>**Prompt:** map intent → destination screen → deeplink URI<br>**Resources:** deeplink catalog & schema, valid URI patterns, naming conventions, fallback rules | **Model** |
| 7 | **Legal Review Pre-screen** — automated compliance triage of the assembled package. | **Tool:** compliance/policy retrieval (RAG over legal playbook + applicable regs) + severity classification<br>**Prompt:** review against playbook, rate severity, output flags + suggested fixes + verdict (pass / needs-review / blocked)<br>**Resources:** marketing legal playbook, approved-claims library, prohibited-terms list, required-disclosure rules, escalation criteria | **Model** |
| 8 | **Final Legal Review** — reviews the pre-screen output, resolves flags, and signs off before launch. | — | **User** |
