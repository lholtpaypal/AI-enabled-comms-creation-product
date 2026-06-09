# BUILD INSTRUCTIONS FOR AI-NATIVE-COMMS-CREATION

## GOAL

This artifact is primarily a communication tool to leadership to illustrate the value, function, inner-workings, and reasoning for an AI-native comms creation process. 

### INSTRUCTIONS

You need to build this as if we're going through the workflow, but you're explaining every step, and why. Remember, the audience is business leaders. This isn't the *actual* prototype, it's just a shell of the prototype that illustrates the value of the solution and secures buy-in.
We'll detail the process necessary to create a 'Recommendation Tile' for the new PayPal app's home feed. The new app is called Oslo. Currently, humans have to do several things to create a Recommendation Tile. They have to ideate and come up with something they believe to be valuable to the user. They have to get a designer to design the actual asset in Figma. They have to write the copy and the call-to-action. They have to work with their engineering team to confirm technical piping for where to send the user, and how. They need to search and filter through our segmentation tool called RPS to select the audience for the recommendation tile. Finally, they need to take the finished design and perform the legal review to ensure everything passes legal inspection. Then, they need to go to our experimenation tool called ELMO to set up A/B testing. Finally, after all that is complete, they have to come to our home-grown creation software called PIE (Personalization Intelligence Engine) to actually create their tile in the system. This last step is fraught with inputs they don't have context for, random text boxes, IDs they need to generate but don't know they need to, etc. It's an absolute pain. This is the perfect use case for an agent-native process. Here's how this might look:

### POTENTIAL AGENTS
0. orchestrator-agent
1. content-writer-agent
2. asset-designer-agent
3. audience-assignment-agent
4. legal-review-agent
5. elmo-experimentation-config-agent

### HYPOTHETICAL WORKFLOW
### HYPOTHETICAL WORKFLOW

A Commerce PM might sit down and have an idea to promote a merchant who's doing an offer on electronics products now through the end of the month. They begin by setting their intent using the text-based creation tool. 

User: "I want to design a tile that encourages the user to buy TVs at Merchant X, now through the end of the month."

---

**Step 1: Intent parsing & orchestration**

The orchestrator agent parses the intent and identifies the four key variables it needs to resolve: *merchant* (Merchant X), *category* (TVs / electronics), *offer window* (now → end of month), and *desired action* (drive purchase). It then dispatches sub-agents in parallel rather than sequentially — a human PM would have to wait on each handoff (designer, copywriter, legal, etc.), but agents can fan out simultaneously and reconcile at the end.

The orchestrator doesn't have to invent the plumbing. Engineering has already built the API mappings and stood up an MCP server that exposes the relevant internal tools — merchant offers, RPS, the Figma plugin, ELMO, PIE — as first-class tool calls. The orchestrator just navigates the MCP server to pick the right sub-agent and tool for each variable it resolved. This is why the agent-native approach is feasible *now* rather than a year from now: the connective tissue already exists.

*Why an agent here, not a human:* A human PM spends hours scheduling kickoffs, writing briefs, and chasing dependencies across 4–5 teams. The orchestrator does this in seconds and never forgets a required input. It also enforces consistency — every tile gets the same structured brief, so downstream agents don't waste cycles asking clarifying questions.

---

**Step 2: `content-writer-agent` drafts copy + CTA**

The content-writer-agent is initialized with PayPal's content guidelines uploaded once as a persistent reference — voice, tone, prohibited phrasing, formatting rules, regional variants. It doesn't re-derive the brand voice on every run; it just applies it. From there, it pulls Merchant X's current offer details from the merchant offers API, references prior high-performing tile copy for electronics (CTR > 2%), and generates 3–5 headline + subhead + CTA variants.

Crucially, the content-writer-agent calls the `legal-review-agent` *inline during drafting*, not after. Every variant is pre-edited to pass legal — the agent checks claim language ("guaranteed," "best price," "save up to"), required disclosures, and merchant trademark usage before the variant is ever surfaced to the PM. By the time the PM sees the copy options, legal has already pre-cleared the language patterns. The dedicated `legal-review-agent` pass in Step 5 then becomes a much lighter final check on the assembled tile, not a substantive content review.

*Why an agent here, not a human:* Copywriters are expensive and slow, and most tile copy is templated variation on proven patterns. An agent grounded in the uploaded brand guidelines generates variants that *start* above the 2% CTR threshold rather than iterating toward it. It produces multiple variants for free (feeding the ELMO test in Step 6), and the inline legal pre-check collapses what is currently a copy → legal → revise → legal again ping-pong into a single pass.

---

**Step 3: `asset-designer-agent` generates the tile visual**

The asset-designer-agent runs on Matt Jakob's Figma plugin, which is already AI-native and has PayPal brand guidelines baked in. The agent doesn't need to reason about color tokens, type scale, safe zones, or component variants from scratch — the plugin enforces all of that natively. The agent just hands it the merchant identity, the approved copy variants from Step 2, and the tile size/placement spec, and the plugin produces compliant Figma files: light/dark mode variants, all copy variants, ready to render.

*Why an agent here, not a human:* Designers shouldn't be spending time on templated tile production — it's mechanical work that doesn't require taste, just adherence to the system. Because Matt's plugin already encodes the system, the agent's job is reduced to passing structured inputs and retrieving outputs. This frees designers to keep evolving the system itself and to work on net-new experiences that *do* require taste. Zero design-system drift, which is the #1 source of QA rework today.

---

**Step 4: `audience-assignment-agent` builds the segment in RPS**

This is the single biggest unlock in the entire workflow — and worth flagging that an agent-native RPS management system is a substantial buildout in its own right, not a thin wrapper. Today, RPS contains thousands of audience lists, and PMs have no practical way to navigate them. They don't know which list to pick, how big any given audience is, who's actually in it, when it was last refreshed, whether it overlaps with another active campaign, or whether the underlying attributes are still being populated by upstream pipelines. So they default to whatever list they used last time, or whatever a teammate recommended in Slack, and precision targeting dies on the vine.

The audience-assignment-agent treats RPS as a queryable knowledge graph rather than a list directory. Given the intent ("users likely to buy a TV at Merchant X this month"), it:

- Translates the intent into candidate attribute filters across the full RPS attribute space (recent electronics browsing, prior Merchant X transactions, BNPL eligibility, geo, etc.)
- Inspects existing audience lists for partial matches and reports each one's size, freshness, composition, and last-used campaign
- Either selects an existing list, composes a new dynamic segment, or recommends a hybrid
- Cross-references the resulting segment against frequency caps and recent exposure to overlapping campaigns (per the Q1'26 Delivery Intelligence foundational checks)
- Surfaces a plain-language summary to the PM: *"~2.3M users, refreshed 6 hours ago, 41% have transacted with Merchant X in the last 90 days, no frequency-cap conflicts"*
- Reserves the segment ID in RPS

*Why an agent here, not a human:* This is the step where humans most visibly hit the wall. The RPS attribute space is too large to hold in a PM's head, and the metadata about each list (size, freshness, composition) is too scattered to manually reconcile under deadline pressure. An agent that can query the full attribute space, evaluate lists by their actual properties rather than their names, and explain its recommendation in plain language doesn't just save time — it produces materially better-targeted audiences than the human baseline. This is the difference between "send to the segment I used last quarter" and "send to the segment most likely to convert on this specific offer."

*Note on scope:* Building this agent properly requires standing up an RPS-native MCP layer that exposes list metadata, attribute lineage, refresh state, and overlap detection as queryable tools. That's a parallel investment, not a free side-effect of the orchestrator.

---

**Step 5: `legal-review-agent` runs final compliance pass**

Because the content-writer-agent in Step 2 already consulted legal-review-agent inline, this step is now a thin final check on the *assembled tile* — copy + creative + offer terms + landing destination, evaluated as a whole. It verifies merchant trademark usage rights against the live merchant contract, confirms required disclosures are rendered correctly in the Figma asset (not just present in copy), and validates regional rules tied to the actual targeted segment from Step 4 (e.g., state-specific finance promo rules now that the geo is known).

Anything ambiguous — and only what's ambiguous — routes to a human legal reviewer with the specific flagged element isolated, not the whole tile.

*Why an agent here, not a human:* ~80% of legal review is pattern-matching against rules that are already written down. Humans should only see the edge cases. Splitting legal into an inline pre-check (Step 2) plus a final assembled-tile check (Step 5) compresses a 3–5 day legal cycle into minutes for the common path. Every human-reviewed escalation feeds back into the agent's rule corpus, so the bar for human escalation keeps rising over time.

---

**Step 6: `elmo-experimentation-config-agent` sets up the A/B test**

The elmo-experimentation-config-agent configures the ELMO experiment: control vs. treatment(s), traffic allocation (starting at the 5K smoke-test population from the GTM process), success metrics (CTR > 2%, click:delete > 1.0, downstream merchant conversion), guardrail metrics (push opt-outs, app uninstalls), and the ramp plan tied to threshold gates. It generates the experiment ID, links it to the tile, and registers the monitoring hooks.

*Why an agent here, not a human:* ELMO setup is where most PMs stall — it's the most technical step and the easiest to misconfigure. Misconfigured experiments produce unreadable results, which means weeks of wasted traffic. An agent that understands the App Comms north-star goals, the threshold framework, and the ELMO schema can stand up a correctly-instrumented experiment every time, with no guesswork on IDs, metric definitions, or ramp logic.

---

**Step 7: Orchestrator assembles everything in PIE**

The orchestrator takes the outputs from Steps 2–6 and writes the tile into PIE via the MCP server: copy variants, asset URLs from the Figma plugin, RPS segment ID, ELMO experiment ID, landing destination (deep link to Merchant X's in-app storefront via webview, per the "Where to land the user?" guidance), start/end dates, and the priority weighting in the home feed ranker. The PM never touches PIE directly.

*Why an agent here, not a human:* PIE is the highest-friction part of the current workflow — it demands inputs PMs don't have context for and IDs they didn't know they'd need. This is exactly the kind of "translate structured intent into structured system inputs" task agents do flawlessly and humans hate. Removing this step alone probably accounts for the majority of the time savings.

---

**Step 8: PM reviews & approves**

The PM is presented with a single review surface: the rendered tile (all variants, light/dark), the target segment summary with estimated reach and composition, the legal status, the ELMO experiment plan with expected read-out timing, and the projected performance range based on comparable historical tiles. They approve, request changes in natural language ("make the headline punchier, drop the exclamation point"), or kill it. Edits route back to the relevant sub-agent only, not through the full pipeline.

*Why a human here, not an agent:* This is the taste-and-judgment checkpoint. The PM owns the strategic call — is this the right merchant to feature this week, does this fit the broader narrative, is the offer compelling enough to spend a notification slot on. Everything upstream of this is mechanical; this step is where human judgment actually adds value.

---

**Step 9: Launch, monitor, and auto-ramp**

Once approved, the orchestrator launches the smoke test to 5K users. It monitors performance against the GTM thresholds (>2% NC CTR, >1.0 click:delete ratio, push opt-outs <0.5% if push-paired) in near real-time. If the tile clears thresholds, it auto-ramps per the pre-configured ELMO plan. If it fails, the orchestrator pauses the tile, summarizes the failure mode (low CTR vs. high dismissal vs. opt-out spike), and proposes specific revisions — usually new copy variants from the content-writer-agent, or a tighter segment from the audience-assignment-agent — without requiring the PM to diagnose the problem from raw dashboards.

*Why an agent here, not a human:* Humans don't watch dashboards in real-time, and certainly not at 2am when a tile is underperforming. The cost of a bad tile compounds every minute it stays live — opt-outs, uninstalls, eroded trust in the channel. An agent watching against pre-defined thresholds can pull a failing tile in minutes and propose the fix before the PM is even back at their desk. This is also what unlocks the "continuous learning" loop in the Q1'26 Delivery Intelligence architecture: every tile's outcome becomes training signal for the next one.

---

### NET IMPACT

What was a 2–3 week, 5-team, 8-handoff process where the PM was the bottleneck on every step becomes a same-day, single-PM workflow where the human shows up twice: once to set intent, once to approve. Everything in between is structured work that agents do faster, more consistently, and with better instrumentation than the human path.

Critically, much of the heavy lifting is *already done or in flight*: engineering has built the MCP layer, content guidelines are uploadable, Matt's Figma plugin is AI-native and brand-aware, and the GTM threshold framework gives the monitoring agent clear gates to enforce. The remaining major investment is the agent-native RPS management system in Step 4 — and that's the step that will deliver the largest single quality improvement, because audience selection is currently where targeting precision is most degraded.

The PM's time is now spent on the parts of the job that actually require a PM — strategy and judgment — rather than on chasing designers, decoding RPS attributes, and fighting PIE's UI.