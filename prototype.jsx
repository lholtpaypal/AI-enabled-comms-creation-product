import { useState, useEffect, useRef } from "react";
import {
  FileText,
  Palette,
  Users,
  Scale,
  FlaskConical,
  CheckCircle2,
  Check,
  RotateCcw,
  Sparkles,
  Cpu,
  X,
  Play,
  Pause,
  SkipBack,
  SkipForward,
} from "lucide-react";

// ─── Script ─────────────────────────────────────────────────────────────────
const INTENT =
  "I want a tile for all users who aren't enrolled in PayPal One Card, encouraging them to sign up for our new debit card.";

const T = {
  typingStart: 800,
  typingEnd: 4500,
  orchestrator: 5000,
  agentsStart: 6700,
  tile: 17400,
  message: 18600,
  checkbox: 19400,
  done: 20000,
};

// Step-through checkpoints — each "Next" jumps to the next meaningful event.
// In production the agents fire in parallel; staggered here so each is visible.
const CHECKPOINTS = [
  0,      // Start
  4800,   // Intent finished typing
  6700,   // Orchestrator complete · content-writer starts
  8700,   // content-writer done · legal-review starts
  10700,  // legal-review done · audience-assignment starts
  13200,  // audience-assignment done · elmo-config starts
  15200,  // elmo-config done · asset-designer starts
  17200,  // asset-designer done · all agents complete
  18800,  // Tile rendered + handoff to Jen Smith
  19600,  // Awaiting legal approval
];

// Inlined PayPal One Card tile screenshot (uploaded by the PM)
const TILE_IMAGE = "data:image/jpeg;base64,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";

const AGENTS = [
  {
    id: "content",
    name: "content-writer",
    display: "Content Writer",
    icon: FileText,
    startAt: 6700,
    doneAt: 8500,
    stages: [
      "Pulling One Card offer details…",
      "Referencing high-CTR financial tiles…",
      "Drafting headline + CTA…",
    ],
    output: "“Earn points with PayPal One Card.”",
    detail: [
      "Pulls One Card offer + brand voice",
      "Generates 3–5 copy variants",
      "Pre-cleared by legal inline",
    ],
    why: [
      "Starts above 2% CTR, doesn't iterate toward it",
      "No copy → legal → revise ping-pong",
    ],
  },
  {
    id: "legal",
    name: "legal-review",
    display: "Legal Review",
    icon: Scale,
    startAt: 8700,
    doneAt: 10500,
    stages: [
      "Checking trademark usage…",
      "Verifying required disclosures…",
      "Validating financial promo rules…",
    ],
    output: "All checks cleared",
    detail: [
      "Pattern-matches assembled tile against the rule corpus",
      "Verifies disclosures, trademarks, regional rules",
      "Escalates only edge cases to a human",
    ],
    why: [
      "3–5 day legal cycle collapses to minutes",
      "Humans see edge cases, not every tile",
    ],
  },
  {
    id: "audience",
    name: "audience-assignment",
    display: "Audience Assignment",
    icon: Users,
    startAt: 10700,
    doneAt: 13000,
    counter: { target: 47.3, unit: "M", suffix: " users" },
    stages: [
      "Filtering: not enrolled in One Card…",
      "Cross-referencing eligibility…",
      "Checking frequency caps…",
    ],
    output: "47.3M users · not yet enrolled",
    detail: [
      "Treats RPS as a queryable knowledge graph",
      "Evaluates lists by composition, freshness, overlap",
      "Reserves the segment automatically",
    ],
    why: [
      "Targets the segment most likely to convert",
      "Not the one you used last quarter",
    ],
  },
  {
    id: "elmo",
    name: "elmo-config",
    display: "ELMO Experiment Config",
    icon: FlaskConical,
    startAt: 13200,
    doneAt: 15000,
    stages: [
      "Generating experiment ID…",
      "Setting success metrics…",
      "Configuring auto-ramp…",
    ],
    output: "5K smoke test · auto-ramp",
    detail: [
      "Configures control, treatments, metrics, guardrails",
      "Sets the auto-ramp plan against threshold gates",
      "Generates the experiment ID",
    ],
    why: [
      "ELMO is where PMs stall most",
      "Misconfigured experiments waste weeks of traffic",
    ],
  },
  {
    id: "design",
    name: "asset-designer",
    display: "Asset Designer",
    icon: Palette,
    startAt: 15200,
    doneAt: 17000,
    stages: [
      "Loading brand tokens…",
      "Rendering light variants…",
      "Rendering dark variants…",
    ],
    output: "6 variants · light + dark",
    detail: [
      "Hands inputs to the brand-aware Figma plugin",
      "Plugin enforces tokens, type scale, safe zones",
      "Produces 6 variants — light + dark",
    ],
    why: [
      "Zero design-system drift",
      "Frees designers for net-new experiences",
    ],
  },
];

// ─── App ────────────────────────────────────────────────────────────────────
export default function App() {
  const [t, setT] = useState(0);
  const [paused, setPaused] = useState(false);
  const [legalApproved, setLegalApproved] = useState(false);
  const [openAgentId, setOpenAgentId] = useState(null);
  const lastFrameRef = useRef(null);

  // Drive the clock — only when not paused
  useEffect(() => {
    if (paused) {
      lastFrameRef.current = null;
      return;
    }
    let id;
    const tick = (now) => {
      if (lastFrameRef.current !== null) {
        const delta = now - lastFrameRef.current;
        setT((prev) => Math.min(T.done + 400, prev + delta));
      }
      lastFrameRef.current = now;
      id = requestAnimationFrame(tick);
    };
    id = requestAnimationFrame(tick);
    return () => {
      cancelAnimationFrame(id);
      lastFrameRef.current = null;
    };
  }, [paused]);

  // Escape closes the modal
  useEffect(() => {
    if (!openAgentId) return;
    const onKey = (e) => e.key === "Escape" && setOpenAgentId(null);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [openAgentId]);

  const openAgent = openAgentId
    ? AGENTS.find((a) => a.id === openAgentId)
    : null;

  // Controls
  const reset = () => {
    setT(0);
    setLegalApproved(false);
    setOpenAgentId(null);
    setPaused(false);
  };

  const stepForward = () => {
    const next = CHECKPOINTS.find((c) => c > t + 80);
    if (next !== undefined) setT(next);
  };

  const stepBack = () => {
    const prev =
      [...CHECKPOINTS].reverse().find((c) => c < t - 200) ?? 0;
    setT(prev);
  };

  const atEnd = t >= CHECKPOINTS[CHECKPOINTS.length - 1] - 50;
  const atStart = t <= 50;

  const typeProg = clamp((t - T.typingStart) / (T.typingEnd - T.typingStart));
  const typed = INTENT.slice(0, Math.floor(INTENT.length * typeProg));
  const typing = t > T.typingStart && t < T.typingEnd;

  const orchActive = t > T.orchestrator;
  const agentsActive = t > T.agentsStart - 200;
  const tileIn = t > T.tile;
  const allDone = t > T.done;

  return (
    <div className="min-h-screen bg-[#FAFAF7] text-black antialiased">
      <Fonts />

      <header className="max-w-2xl mx-auto px-6 pt-10 pb-4 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2.5">
          <div className="w-6 h-6 rounded-md bg-black flex items-center justify-center">
            <div className="w-2 h-2 rounded-full bg-[#60CDFF]" />
          </div>
          <div className="text-[12px] font-mono text-black/55 tracking-wide">
            Oslo · Comms Studio
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Step controls cluster */}
          <div className="flex items-center bg-white border border-black/10 rounded-full overflow-hidden">
            <button
              onClick={stepBack}
              disabled={atStart}
              className="w-8 h-8 flex items-center justify-center hover:bg-black/[0.04] disabled:opacity-30 disabled:hover:bg-transparent transition"
              title="Previous step"
            >
              <SkipBack className="w-3.5 h-3.5 text-black/70" />
            </button>
            <button
              onClick={() => setPaused((p) => !p)}
              disabled={atEnd && !paused}
              className="w-8 h-8 flex items-center justify-center hover:bg-black/[0.04] disabled:opacity-30 disabled:hover:bg-transparent transition border-l border-black/10"
              title={paused ? "Play" : "Pause"}
            >
              {paused ? (
                <Play className="w-3.5 h-3.5 text-black/75 fill-black/75" />
              ) : (
                <Pause className="w-3.5 h-3.5 text-black/75 fill-black/75" />
              )}
            </button>
            <button
              onClick={stepForward}
              disabled={atEnd}
              className="w-8 h-8 flex items-center justify-center hover:bg-black/[0.04] disabled:opacity-30 disabled:hover:bg-transparent transition border-l border-black/10"
              title="Next step"
            >
              <SkipForward className="w-3.5 h-3.5 text-black/70" />
            </button>
          </div>

          <button
            onClick={reset}
            className="text-[11px] font-mono text-black/55 hover:text-black transition flex items-center gap-1.5 px-3 h-8 rounded-full border border-black/10 hover:border-black/40"
            title="Reset to start"
          >
            <RotateCcw className="w-3 h-3" />
            Reset
          </button>
        </div>
      </header>

      <main className="max-w-2xl mx-auto px-6 pb-24">
        <Step number="1" title="You ask for what you want">
          <IntentBox typed={typed} typing={typing} />
        </Step>

        <Step number="2" title="The orchestrator dispatches" show={orchActive}>
          <OrchestratorLine t={t} />
        </Step>

        <Step
          number="3"
          title="Five agents work in parallel"
          show={agentsActive}
        >
          <div className="space-y-2">
            {AGENTS.map((a) => (
              <AgentRow
                key={a.id}
                agent={a}
                t={t}
                onOpen={() => setOpenAgentId(a.id)}
              />
            ))}
          </div>
          <div className="mt-3 text-[11px] font-mono text-black/40 text-center">
            Tap any agent to see how it works · staggered for the demo (in production they run in parallel)
          </div>
        </Step>

        <Step number="4" title="Your tile is ready" show={tileIn}>
          <Tile />
          <JenMessage visible={t > T.message} />
          <LaunchControls
            visible={t > T.checkbox}
            legalApproved={legalApproved}
            setLegalApproved={setLegalApproved}
          />
        </Step>
      </main>

      <AgentModal agent={openAgent} onClose={() => setOpenAgentId(null)} />
    </div>
  );
}

// ─── Step container ─────────────────────────────────────────────────────────
function Step({ number, title, children, show = true }) {
  return (
    <section
      className={`pt-10 transition-all duration-500 ${
        show
          ? "opacity-100 translate-y-0"
          : "opacity-0 translate-y-3 pointer-events-none"
      }`}
    >
      <div className="flex items-baseline gap-3 mb-4">
        <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-black/40">
          Step {number}
        </span>
        <h2 className="font-serif text-[22px] tighter leading-none">{title}</h2>
      </div>
      {children}
    </section>
  );
}

// ─── Intent box ─────────────────────────────────────────────────────────────
function IntentBox({ typed, typing }) {
  return (
    <div className="border border-black/10 bg-white rounded-2xl p-5 shadow-[0_2px_12px_rgba(0,0,0,0.04)]">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-5 h-5 rounded-full bg-black flex items-center justify-center text-white text-[9px] font-mono">
          PM
        </div>
        <span className="text-[10px] font-mono uppercase tracking-[0.16em] text-black/50">
          PM · PayPal Debit Card team
        </span>
      </div>
      <p className="font-serif text-[20px] leading-[1.35] min-h-[80px]">
        {typed || (
          <span className="text-black/25 italic">Waiting for intent…</span>
        )}
        {typing && (
          <span className="inline-block w-[2px] h-[18px] bg-[#002991] ml-0.5 align-middle animate-pulse" />
        )}
      </p>
    </div>
  );
}

// ─── Orchestrator line ──────────────────────────────────────────────────────
function OrchestratorLine({ t }) {
  const done = t > T.agentsStart;
  return (
    <div className="border border-black/10 bg-white rounded-2xl p-4 flex items-center gap-3">
      <div className="w-7 h-7 rounded-md bg-black flex items-center justify-center shrink-0">
        <Cpu className="w-3.5 h-3.5 text-[#60CDFF]" />
      </div>
      <div className="flex-1 min-w-0">
        <div className="text-[10px] font-mono uppercase tracking-[0.16em] text-black/50">
          orchestrator-agent
        </div>
        <div className="text-[13px] mt-0.5">
          {done ? (
            <span className="text-black/85">
              Parsed intent · dispatched 5 sub-agents
            </span>
          ) : (
            <span className="text-black/60">
              Resolving merchant, category, window, action…
            </span>
          )}
        </div>
      </div>
      {done ? (
        <CheckCircle2 className="w-4 h-4 text-[#002991] shrink-0" />
      ) : (
        <Spinner />
      )}
    </div>
  );
}

// ─── Agent row ──────────────────────────────────────────────────────────────
function AgentRow({ agent, t, onOpen }) {
  const Icon = agent.icon;
  const started = t > agent.startAt;
  const done = t > agent.doneAt;
  const working = started && !done;

  const progress = started
    ? clamp((t - agent.startAt) / (agent.doneAt - agent.startAt))
    : 0;

  const stageIdx = Math.min(
    agent.stages.length - 1,
    Math.floor(progress * agent.stages.length),
  );

  let liveText;
  if (done) {
    liveText = agent.output;
  } else if (working && agent.counter) {
    const n = (agent.counter.target * progress).toFixed(1);
    liveText = `Scanned ${n}${agent.counter.unit}${agent.counter.suffix}…`;
  } else if (working) {
    liveText = agent.stages[stageIdx];
  } else {
    liveText = "Queued";
  }

  return (
    <button
      onClick={onOpen}
      className={`group w-full text-left border rounded-xl bg-white px-4 pt-3 pb-3 transition-all duration-300 cursor-pointer hover:border-[#002991]/50 hover:shadow-[0_4px_18px_rgba(0,41,145,0.12)] ${
        done
          ? "border-black/10"
          : working
            ? "border-[#002991]/40 shadow-[0_2px_14px_rgba(0,41,145,0.10)]"
            : "border-black/8 opacity-70"
      }`}
    >
      <div className="flex items-center gap-3.5">
        <div
          className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 transition-colors ${
            done
              ? "bg-black text-white"
              : working
                ? "bg-[#002991] text-white"
                : "bg-black/[0.04] text-black/70"
          }`}
        >
          <Icon className="w-4 h-4" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="text-[10px] font-mono text-black/45 leading-none mb-1.5">
            {agent.name}
          </div>
          <div
            key={`${agent.id}-${done ? "done" : stageIdx}`}
            className={`text-[13px] tight leading-tight transition-colors fade-in ${
              done ? "text-black font-medium" : "text-black/75"
            }`}
          >
            {liveText}
          </div>
        </div>

        <div className="shrink-0">
          {done ? (
            <CheckCircle2 className="w-4 h-4 text-[#002991]" />
          ) : working ? (
            <Spinner />
          ) : (
            <div className="w-3 h-3 rounded-full border border-black/15" />
          )}
        </div>
      </div>

      {/* Progress bar */}
      <div className="mt-3 h-[2px] bg-black/[0.06] rounded-full overflow-hidden">
        <div
          className={`h-full transition-[width] duration-200 ease-linear ${
            done ? "bg-black" : "bg-[#002991]"
          }`}
          style={{ width: `${progress * 100}%` }}
        />
      </div>
    </button>
  );
}

// ─── Agent modal ────────────────────────────────────────────────────────────
function AgentModal({ agent, onClose }) {
  if (!agent) return null;
  const Icon = agent.icon;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-5 backdrop-fade"
      onClick={onClose}
    >
      <div className="absolute inset-0 bg-black/45 backdrop-blur-[3px]" />
      <div
        className="relative bg-white rounded-2xl max-w-[440px] w-full p-7 shadow-[0_20px_60px_rgba(0,0,0,0.25)] modal-pop"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close */}
        <button
          onClick={onClose}
          className="absolute top-3.5 right-3.5 w-8 h-8 rounded-full hover:bg-black/[0.06] flex items-center justify-center transition"
          aria-label="Close"
        >
          <X className="w-4 h-4 text-black/65" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-6 pr-10">
          <div className="w-11 h-11 rounded-xl bg-black text-white flex items-center justify-center shrink-0">
            <Icon className="w-5 h-5" />
          </div>
          <div className="min-w-0">
            <div className="text-[10px] font-mono uppercase tracking-[0.18em] text-black/50 leading-none mb-1.5">
              {agent.name}
            </div>
            <div className="font-serif text-[22px] tighter leading-none">
              {agent.display}
            </div>
          </div>
        </div>

        {/* How it works */}
        <div className="mb-5">
          <div className="text-[10px] uppercase tracking-[0.18em] font-mono text-black/55 mb-3">
            How it works
          </div>
          <ul className="space-y-2">
            {agent.detail.map((item, i) => (
              <li
                key={i}
                className="flex items-start gap-2.5 text-[13.5px] leading-[1.45] text-black/80"
              >
                <span className="w-1 h-1 rounded-full bg-black/40 shrink-0 mt-[9px]" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Why an agent */}
        <div className="border-t border-black/8 pt-5 -mx-7 px-7 bg-[#FAFAF7] -mb-7 rounded-b-2xl pb-7">
          <div className="text-[10px] uppercase tracking-[0.18em] font-mono text-[#002991] mb-3 flex items-center gap-1.5">
            <Sparkles className="w-3 h-3" />
            Why an agent, not a human
          </div>
          <ul className="space-y-2">
            {agent.why.map((item, i) => (
              <li
                key={i}
                className="flex items-start gap-2.5 text-[13.5px] leading-[1.45] text-black/85"
              >
                <span className="w-1 h-1 rounded-full bg-[#002991] shrink-0 mt-[9px]" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

// ─── Tile (PayPal One Card — uploaded image) ────────────────────────────────
function Tile() {
  return (
    <div className="flex justify-center">
      <div
        className="rounded-2xl overflow-hidden tile-pop bg-[#0E1638] w-full max-w-[300px]"
        style={{ boxShadow: "0 16px 48px rgba(14,22,56,0.28)" }}
      >
        <img
          src={TILE_IMAGE}
          alt="PayPal One Card tile"
          className="w-full h-auto block"
        />
      </div>
    </div>
  );
}

// ─── Jen Smith message ──────────────────────────────────────────────────────
function JenMessage({ visible }) {
  return (
    <div
      className={`mt-4 border border-[#002991]/15 bg-white rounded-2xl p-4 flex items-start gap-3 transition-all duration-500 ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2 pointer-events-none"
      }`}
    >
      <Sparkles className="w-4 h-4 text-[#002991] shrink-0 mt-0.5" />
      <div className="flex-1 text-[13px] leading-[1.55] text-black/85">
        <span className="font-medium">Great — your tile is created.</span>{" "}
        Your legal point-of-contact is{" "}
        <span className="font-medium text-[#002991]">Jen Smith</span>. Take this
        file to her for legal approval.
      </div>
    </div>
  );
}

// ─── Legal approval toggle + Approve & launch ───────────────────────────────
function LaunchControls({ visible, legalApproved, setLegalApproved }) {
  return (
    <div
      className={`mt-3 transition-all duration-500 ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2 pointer-events-none"
      }`}
    >
      <button
        onClick={() => setLegalApproved(!legalApproved)}
        className="w-full border border-black/10 bg-white rounded-2xl p-4 flex items-center gap-3 hover:border-black/30 transition text-left"
      >
        <div
          className={`w-5 h-5 rounded-md border-2 flex items-center justify-center shrink-0 transition-all ${
            legalApproved
              ? "bg-[#002991] border-[#002991]"
              : "bg-white border-black/25"
          }`}
        >
          {legalApproved && <Check className="w-3.5 h-3.5 text-white" strokeWidth={3} />}
        </div>
        <div className="flex-1 text-[13px] leading-snug">
          <span className={legalApproved ? "text-black font-medium" : "text-black/75"}>
            Legal approval received from Jen Smith
          </span>
        </div>
      </button>

      <button
        disabled={!legalApproved}
        className={`mt-3 w-full rounded-2xl px-5 py-4 text-[14px] font-medium transition-all flex items-center justify-center gap-2 ${
          legalApproved
            ? "bg-black hover:bg-[#002991] text-white shadow-[0_4px_16px_rgba(0,41,145,0.18)] cursor-pointer"
            : "bg-black/[0.06] text-black/35 cursor-not-allowed"
        }`}
      >
        {legalApproved && <Sparkles className="w-3.5 h-3.5" />}
        Approve &amp; launch smoke test
      </button>
    </div>
  );
}

// ─── Bits ───────────────────────────────────────────────────────────────────
function Spinner() {
  return (
    <div className="relative w-4 h-4">
      <div className="absolute inset-0 rounded-full border-2 border-black/10" />
      <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-[#002991] spin" />
    </div>
  );
}

function clamp(x) {
  return Math.max(0, Math.min(1, x));
}

function Fonts() {
  return (
    <style>{`
      @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Geist:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
      :root, body { font-family: 'Geist', system-ui, sans-serif; }
      .font-serif { font-family: 'Instrument Serif', Georgia, serif; font-weight: 400; }
      .font-mono { font-family: 'JetBrains Mono', Menlo, monospace; }
      .tight { letter-spacing: -0.025em; }
      .tighter { letter-spacing: -0.04em; }

      @keyframes spin { to { transform: rotate(360deg); } }
      .spin { animation: spin 0.9s linear infinite; }

      @keyframes fade-in {
        from { opacity: 0; transform: translateY(2px); }
        to   { opacity: 1; transform: translateY(0); }
      }
      .fade-in { animation: fade-in 0.22s ease-out; }

      @keyframes tile-pop {
        0%   { opacity: 0; transform: scale(0.94) translateY(8px); }
        60%  { opacity: 1; transform: scale(1.02) translateY(0); }
        100% { opacity: 1; transform: scale(1) translateY(0); }
      }
      .tile-pop { animation: tile-pop 0.65s cubic-bezier(0.2, 0.7, 0.3, 1.1); }

      @keyframes backdrop-fade {
        from { opacity: 0; }
        to   { opacity: 1; }
      }
      .backdrop-fade { animation: backdrop-fade 0.18s ease-out; }

      @keyframes modal-pop {
        from { opacity: 0; transform: scale(0.96) translateY(6px); }
        to   { opacity: 1; transform: scale(1) translateY(0); }
      }
      .modal-pop { animation: modal-pop 0.24s cubic-bezier(0.2, 0.7, 0.3, 1.05); }
    `}</style>
  );
}
