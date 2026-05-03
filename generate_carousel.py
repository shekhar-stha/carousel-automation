#!/usr/bin/env python3
"""
Carousel Generator — runs on GitHub Actions (remote, laptop-independent).
Uses Tavily to research current Instagram trends, then calls Claude API
to think, decide the best topic, and generate a full carousel-light HTML.
Deploys to Vercel via REST API.
"""

import os, sys, json, base64, urllib.request, urllib.parse
from datetime import datetime, timezone

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
VERCEL_TOKEN      = os.environ["VERCEL_TOKEN"]
TAVILY_API_KEY    = os.environ["TAVILY_API_KEY"]
RUN_SESSION       = os.environ.get("RUN_SESSION", "morning")  # morning | afternoon

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
DAY_NAME = datetime.now(timezone.utc).strftime("%A")

# ─────────────────────────────────────────────
# 1. RESEARCH — Tavily web search
# ─────────────────────────────────────────────

def tavily_search(query: str, max_results: int = 5) -> list[dict]:
    payload = json.dumps({
        "api_key": TAVILY_API_KEY,
        "query": query,
        "search_depth": "advanced",
        "max_results": max_results,
        "include_answer": True
    }).encode()
    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        resp = json.loads(urllib.request.urlopen(req, timeout=20).read())
        return resp.get("results", [])
    except Exception as e:
        print(f"Tavily search failed for '{query}': {e}")
        return []

print("🔍 Researching current Instagram trends...")

searches = [
    "Instagram content strategy trends 2026 service-based business owners",
    "Instagram reels hooks that go viral 2026 coaches consultants",
    "Instagram growth organic reach algorithm changes 2026",
]

research_results = []
for q in searches:
    results = tavily_search(q, max_results=4)
    for r in results:
        research_results.append({
            "query": q,
            "title": r.get("title", ""),
            "snippet": r.get("content", "")[:400],
            "url": r.get("url", "")
        })

research_text = "\n\n".join([
    f"[{r['query']}]\n{r['title']}\n{r['snippet']}"
    for r in research_results[:12]
])

print(f"  Found {len(research_results)} research snippets")

# ─────────────────────────────────────────────
# 2. BRAND KNOWLEDGE (embedded)
# ─────────────────────────────────────────────

BRAND_VOICE = """
BRAND: Shekhar Shrestha (@marketing.shekhar) — Instagram Growth Strategist, Orcalynx Agency
AUDIENCE: Service-based business owners — coaches, consultants, agency owners

VOICE PILLARS:
- Analytical yet accessible — complex strategies broken into actionable frameworks
- Results-focused — direct about what works, validates struggles, pivots to solutions
- Confident yet humble — leads with "we" and "our clients", not "I"
- Specific over general — "388K followers in 1.5 years" not "massive growth"

CORE POSITIONING:
- Grew clients from 0 to 388K followers organically
- Methodology: research-backed > random posting, strategic > constant posting, results > vanity metrics
- "You're not failing at Instagram. Your strategy is."
- "Research-based, not random."

CONTENT PRINCIPLES:
- Organic only — never mention paid ads
- Systems over hacks — repeatable frameworks, not quick fixes
- Business outcomes over follower vanity
- 3-month minimum timelines (never promise overnight results)
- En dash – not em dash —
- Never "Follow for more" — always "Follow @marketing.shekhar"
- Use "we" / "our clients" — never "I"

DISTINCTIVE PHRASES TO USE:
- "Here's what most people miss:"
- "The research shows:"
- "Our clients see this pattern:"
- "That's costing you leads."
- "Most business owners do [X]. That's backwards."
- "You're not failing at Instagram. Your strategy is."

CAROUSEL ANATOMY:
- 6–8 slides for a standard educational carousel
- S1: Cover/Hook — stop the scroll, curiosity or polarizing promise, "Swipe →" cue
- S2: Context — why this matters, often a contrast (what most do vs what works) or a big stat
- S3–S6: Step/Framework slides — each has one clear point, chip label, visual component
- Final: CTA — one action (comment keyword), follow bar "@marketing.shekhar"

HOOK FORMULA BANK (pick one per carousel):
- Contrarian: "Stop [common advice]. Do [opposite] instead."
- Number: "388K followers in 18 months — here's the exact system."
- Identity: "If you're a coach posting daily and still under 5K, this is why."
- Curiosity: "I was about to lose the client when I discovered this."
- Before/after: "6 months ago: invisible. Today: 3 discovery calls a week."
- Expose: "93% of creators get the first slide wrong."
"""

DESIGN_SYSTEM = """
CAROUSEL-LIGHT DESIGN SYSTEM (cream/warm paper format):

CSS VARIABLES:
--bg: #F2EADB (warm paper cream — main slide background)
--bg-2: #EBE2D0
--panel: #FFFFFF (card backgrounds)
--panel-2: #FAF6EC
--line: #E0D5BD
--line-2: #D4C7A8
--ink: #1A1410 (deep warm black — all body text)
--ink-soft: #2D241D (slightly softer for lede/descriptions)
--muted: #8A7C68 (labels, step numbers)
--amber: #F2A93B (THE accent — highlights, chips, CTA)
--amber-deep: #C9844A (slightly deeper amber for contrast)
--code-bg: #1A1410
--code-fg: #F2EADB

SUN-GLOW GRADIENT (every slide — copy exactly):
.slide::before {
  content:""; position:absolute; inset:0;
  background:
    radial-gradient(ellipse 100% 60% at 50% 0%, rgba(242,169,59,0.18), transparent 65%),
    radial-gradient(ellipse 80% 50% at 100% 100%, rgba(201,132,74,0.10), transparent 70%);
  pointer-events:none; z-index:0;
}

TYPOGRAPHY (binding rules):
- Coolvetica: ONLY for headlines ≥40px (h1, h2, big numbers)
- -apple-system bold: everything ≤28px (chips, labels, body, rows)
- Arrow characters (→): MUST use system font, not Coolvetica
- NEVER opacity:0.5 on text — use a dimmer color variable instead

SLIDE COMPONENTS TO USE (pick different ones per slide, never repeat adjacent):

1. STEP CARDS (vertical list with numbered circles):
<div class="step-list">
  <div class="step-card hi"> <!-- hi = amber highlight on active -->
    <div class="s-num">1</div>
    <div class="s-body">
      <div class="s-title">Title here</div>
      <div class="s-desc">Description here</div>
    </div>
  </div>
</div>

2. FRAMEWORK ROWS (label + description pairs):
<div class="fw-list">
  <div class="fw-row hi">
    <div class="fw-lbl">LABEL</div>
    <div class="fw-desc">Description text here</div>
  </div>
</div>

3. 2x2 GRID CARDS:
<div class="grid-2x2">
  <div class="g-card">
    <div class="gc-icon">📱</div>
    <div class="gc-label">STEP LABEL</div>
    <div class="gc-title">Card title</div>
    <div class="gc-note">Supporting note</div>
  </div>
</div>

4. CONTRAST PAIR (bad vs good):
<div class="contrast-pair">
  <div class="c-panel bad"><div class="c-tag">❌ What most do</div><div class="c-text">Negative example</div></div>
  <div class="c-panel good"><div class="c-tag">✅ What works</div><div class="c-text">Positive example</div></div>
</div>

5. BIG STAT:
<div class="big-stat">
  <div class="bs-num">388K</div>
  <div class="bs-label">Followers in 18 months</div>
  <div class="bs-note">Without running a single paid ad.</div>
</div>

6. WEEKLY SCHEDULE:
<div class="week-title">The weekly system:</div>
<div class="week-days">
  <div class="w-day"><div class="d-name">Monday</div><div class="d-task">Task description</div></div>
</div>

COVER SLIDE PATTERN:
<div class="slide" id="s1">
  <div class="pad cover">
    <div class="badge"><span class="dot"></span>EYEBROW LABEL</div>
    <h1>Headline with one <em>amber word</em> highlighted</h1>
    <p class="sub">Supporting sub-line — 1 sentence, specific.</p>
    <div class="swipe-cue">Swipe to see the system →</div>
  </div>
</div>

BODY SLIDE PATTERN:
<div class="slide" id="sN">
  <div class="pad body-slide">
    <div class="head-row"><span class="chip">Step 01</span><span class="of-label">of 04</span></div>
    <h2>Headline with <span class="hl">key word</span></h2>
    <p class="lede">2–3 sentence explanation. Specific and actionable.</p>
    <!-- ONE visual component here -->
  </div>
</div>

CTA SLIDE PATTERN:
<div class="slide" id="sN">
  <div class="pad cta">
    <div class="badge"><span class="dot"></span>FREE GUIDE</div>
    <h2>Want the full <em>system</em>?</h2>
    <p class="sub-cta">What they'll get — specific.</p>
    <div class="actions">
      <div class="act-line">Comment <code>KEYWORD</code> and we'll send you [specific thing].</div>
    </div>
    <div class="follow"><div class="fh">Follow @marketing.shekhar</div><div class="arr">→</div></div>
  </div>
</div>

CTA KEYWORDS — map to real Orcalynx free resources at orcalynx.com/resources:
Pick the keyword that best fits the carousel topic. Each keyword unlocks a real resource.

| Comment Keyword | Resource Name                  | What they get                                              |
|-----------------|--------------------------------|------------------------------------------------------------|
| PLAYBOOK        | Instagram Growth Playbook      | 12-chapter step-by-step guide — niche, hooks, 5X Outlier Rule, funnels, 30-day checklist |
| FORMULA         | Viral Content Formula          | Full short-form content engine — hook templates, angle frameworks, script builders across 6 niches |
| HOOKS           | 1,000 Viral Hooks              | Searchable hook library — 1,000+ templates across 7 categories, linked to real reels |
| FUNNEL          | Instagram Content Funnel       | Top/mid/bottom-funnel content guide — content idea generator, 72 ready-to-film ideas |
| TRIAL           | Trial Reels Playbook           | Outlier Repost method, Remix Trick, A/B Hook Testing — maximize reel performance |
| PROFILE         | Fix Your Instagram Profile     | Interactive profile optimization — SEO name field, bio framework, link strategy, bio builder |
| STORYTELLING    | Storytelling for Social Media  | 7 story types with script templates, but/therefore framework, story rhythm and tone |

Always pick the keyword whose resource is most directly useful for the carousel's specific topic.
Example: a hooks/viral content carousel → HOOKS or FORMULA; a profile/growth carousel → PLAYBOOK or PROFILE.
"""

FULL_CSS = """
<style>
@font-face{font-family:'Coolvetica';src:local('Coolvetica');font-weight:400;}
:root{
  --bg:#F2EADB;--bg-2:#EBE2D0;--panel:#FFFFFF;--panel-2:#FAF6EC;
  --line:#E0D5BD;--line-2:#D4C7A8;
  --ink:#1A1410;--ink-soft:#2D241D;--muted:#8A7C68;
  --amber:#F2A93B;--amber-soft:#F4B665;--amber-deep:#C9844A;
  --code-bg:#1A1410;--code-fg:#F2EADB;
  --mono:ui-monospace,'SF Mono',Menlo,monospace;
}
*{box-sizing:border-box;margin:0;padding:0;}
body{background:#E5DCC4;font-family:'Coolvetica','Helvetica Neue',sans-serif;color:var(--ink);}
.page-header{text-align:center;padding:24px 20px 10px;font-family:-apple-system,sans-serif;font-weight:700;font-size:13px;color:var(--muted);letter-spacing:0.08em;text-transform:uppercase;}
.deck{display:flex;flex-direction:column;align-items:center;gap:28px;padding:6px 20px 80px;}
.slide{width:1080px;height:1350px;background:var(--bg);position:relative;overflow:hidden;border-radius:4px;box-shadow:0 12px 40px rgba(26,20,16,0.18);}
.slide::before{content:"";position:absolute;inset:0;background:radial-gradient(ellipse 100% 60% at 50% 0%,rgba(242,169,59,0.18),transparent 65%),radial-gradient(ellipse 80% 50% at 100% 100%,rgba(201,132,74,0.10),transparent 70%);pointer-events:none;z-index:0;}
.slide .pad{padding:90px 84px;height:100%;display:flex;flex-direction:column;position:relative;z-index:1;}
.foot{position:absolute;left:84px;right:84px;bottom:60px;display:flex;justify-content:flex-end;z-index:2;}
.foot .swipe{font-family:-apple-system,sans-serif;font-size:24px;font-weight:700;color:var(--amber-deep);}
.head-row{display:flex;align-items:center;gap:22px;font-family:-apple-system,sans-serif;}
.chip{background:var(--ink);color:var(--amber);padding:10px 22px;border-radius:999px;font-weight:800;letter-spacing:0.1em;font-size:22px;text-transform:uppercase;}
.of-label{color:var(--muted);font-size:22px;letter-spacing:0.1em;font-weight:600;text-transform:uppercase;}
.hl{background:var(--amber);color:var(--ink);padding:4px 12px;border-radius:6px;box-decoration-break:clone;-webkit-box-decoration-break:clone;}
/* COVER */
.cover .badge{display:inline-flex;align-items:center;gap:10px;padding:10px 18px;background:var(--ink);border-radius:999px;font-family:-apple-system,sans-serif;font-weight:700;font-size:21px;letter-spacing:0.1em;text-transform:uppercase;color:var(--bg);width:fit-content;margin-bottom:44px;}
.cover .badge .dot{width:9px;height:9px;border-radius:50%;background:var(--amber);flex-shrink:0;}
.cover h1{font-family:'Coolvetica','Helvetica Neue',sans-serif;font-size:136px;line-height:0.95;letter-spacing:-0.02em;font-weight:400;color:var(--ink);}
.cover h1 em{font-style:normal;background:var(--amber);color:var(--ink);padding:0 14px;border-radius:8px;display:inline-block;line-height:1.05;}
.cover .sub{margin-top:34px;font-family:-apple-system,sans-serif;font-size:34px;line-height:1.4;color:var(--ink-soft);max-width:820px;}
.cover .swipe-cue{margin-top:30px;font-family:-apple-system,sans-serif;font-size:28px;font-weight:700;color:var(--amber-deep);}
/* BODY */
.body-slide h2{font-family:'Coolvetica','Helvetica Neue',sans-serif;font-size:90px;font-weight:400;line-height:1.06;margin-top:28px;color:var(--ink);}
.body-slide .lede{margin-top:24px;font-family:-apple-system,sans-serif;font-size:30px;line-height:1.46;color:var(--ink-soft);max-width:900px;}
/* STEP CARDS */
.step-list{display:flex;flex-direction:column;gap:16px;margin-top:28px;flex:1;justify-content:center;}
.step-card{background:var(--panel);border:1.5px solid var(--line);border-radius:18px;padding:24px 30px;display:flex;align-items:flex-start;gap:22px;box-shadow:0 2px 8px rgba(26,20,16,0.05);}
.step-card.hi{border-color:var(--amber);box-shadow:0 4px 18px rgba(242,169,59,0.12);}
.s-num{width:52px;height:52px;background:var(--ink);border-radius:50%;display:flex;align-items:center;justify-content:center;font-family:'Coolvetica','Helvetica Neue',sans-serif;font-size:30px;color:var(--amber);flex-shrink:0;}
.step-card.hi .s-num{background:var(--amber);color:var(--ink);}
.s-title{font-family:-apple-system,sans-serif;font-size:27px;font-weight:800;color:var(--ink);line-height:1.2;}
.s-desc{font-family:-apple-system,sans-serif;font-size:24px;color:var(--ink-soft);margin-top:6px;line-height:1.4;}
/* FRAMEWORK ROWS */
.fw-list{display:flex;flex-direction:column;gap:16px;margin-top:26px;flex:1;justify-content:center;}
.fw-row{background:var(--panel);border:1.5px solid var(--line);border-radius:16px;padding:22px 28px;display:flex;align-items:flex-start;gap:20px;box-shadow:0 2px 6px rgba(26,20,16,0.04);}
.fw-row.hi{border-color:var(--amber);box-shadow:0 4px 16px rgba(242,169,59,0.10);}
.fw-lbl{font-family:-apple-system,sans-serif;font-size:21px;font-weight:800;color:var(--amber-deep);text-transform:uppercase;letter-spacing:0.08em;min-width:190px;flex-shrink:0;padding-top:2px;}
.fw-desc{font-family:-apple-system,sans-serif;font-size:26px;color:var(--ink-soft);line-height:1.42;}
/* 2x2 GRID */
.grid-2x2{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:24px;flex:1;}
.g-card{background:var(--panel);border:1.5px solid var(--line);border-radius:18px;padding:26px;display:flex;flex-direction:column;gap:10px;box-shadow:0 2px 8px rgba(26,20,16,0.05);}
.gc-icon{font-size:44px;line-height:1;}
.gc-label{font-family:-apple-system,sans-serif;font-size:17px;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;color:var(--amber-deep);}
.gc-title{font-family:-apple-system,sans-serif;font-size:25px;font-weight:800;color:var(--ink);line-height:1.2;}
.gc-note{font-family:-apple-system,sans-serif;font-size:22px;color:var(--muted);line-height:1.35;}
/* CONTRAST PAIR */
.contrast-pair{display:flex;flex-direction:column;gap:14px;margin-top:28px;flex:1;justify-content:center;}
.c-panel{border-radius:18px;padding:28px 32px;}
.c-panel.bad{background:#FFF5F5;border:1.5px solid #F5C5C5;}
.c-panel.bad .c-tag{background:#E03E3E;color:#fff;}
.c-panel.good{background:var(--panel-2);border:1.5px solid var(--amber);}
.c-panel.good .c-tag{background:var(--amber);color:var(--ink);}
.c-tag{display:inline-block;font-family:-apple-system,sans-serif;font-size:18px;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;padding:6px 14px;border-radius:999px;margin-bottom:14px;}
.c-text{font-family:-apple-system,sans-serif;font-size:26px;color:var(--ink-soft);line-height:1.44;}
.c-text strong{color:var(--ink);font-weight:800;}
/* BIG STAT */
.big-stat{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;text-align:center;margin-top:20px;}
.bs-num{font-family:'Coolvetica','Helvetica Neue',sans-serif;font-size:200px;line-height:0.9;color:var(--ink);letter-spacing:-0.03em;}
.bs-label{font-family:-apple-system,sans-serif;font-size:32px;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted);}
.bs-note{font-family:-apple-system,sans-serif;font-size:28px;color:var(--ink-soft);line-height:1.4;max-width:700px;}
/* WEEKLY SCHEDULE */
.week-title{font-family:-apple-system,sans-serif;font-size:26px;font-weight:800;text-transform:uppercase;letter-spacing:0.1em;color:var(--muted);margin-top:26px;border-bottom:2px solid var(--amber);padding-bottom:12px;}
.week-days{display:flex;flex-direction:column;flex:1;margin-top:4px;justify-content:center;}
.w-day{padding:17px 0;border-bottom:1px solid var(--line);}
.w-day:last-child{border-bottom:none;}
.d-name{font-family:-apple-system,sans-serif;font-size:25px;font-weight:800;color:var(--amber-deep);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;}
.d-task{font-family:-apple-system,sans-serif;font-size:25px;color:var(--ink-soft);line-height:1.38;font-style:italic;}
/* CTA */
.cta .badge{display:inline-flex;align-items:center;gap:10px;padding:9px 18px;background:var(--ink);border-radius:999px;font-family:-apple-system,sans-serif;font-weight:700;font-size:21px;letter-spacing:0.1em;text-transform:uppercase;color:var(--bg);width:fit-content;margin-bottom:26px;}
.cta .badge .dot{width:9px;height:9px;border-radius:50%;background:var(--amber);flex-shrink:0;}
.cta h2{font-family:'Coolvetica','Helvetica Neue',sans-serif;font-size:118px;line-height:0.97;font-weight:400;color:var(--ink);}
.cta h2 em{font-style:normal;color:var(--amber-deep);}
.cta .sub-cta{margin-top:20px;font-family:-apple-system,sans-serif;font-size:30px;color:var(--ink-soft);line-height:1.46;max-width:840px;}
.cta .actions{margin-top:32px;padding:30px 36px;background:var(--panel);border-radius:22px;border-left:8px solid var(--amber);box-shadow:0 6px 20px rgba(26,20,16,0.07);}
.act-line{font-family:-apple-system,sans-serif;font-size:28px;color:var(--ink-soft);line-height:1.52;}
.cta .actions code{background:var(--amber);padding:2px 10px;border-radius:6px;font-family:var(--mono);font-size:28px;font-weight:700;color:var(--ink);}
.cta .follow{margin-top:auto;background:var(--ink);color:var(--bg);padding:32px 42px;border-radius:22px;display:flex;justify-content:space-between;align-items:center;}
.fh{font-family:'Coolvetica','Helvetica Neue',sans-serif;font-size:52px;color:var(--bg);}
.arr{font-family:-apple-system,sans-serif;font-size:52px;color:var(--amber);font-weight:700;}
</style>
"""

# ─────────────────────────────────────────────
# 3. CALL CLAUDE API — research → think → generate
# ─────────────────────────────────────────────

print("🤖 Calling Claude to think, decide topic, and generate carousel...")

session_label = "morning" if RUN_SESSION == "morning" else "afternoon"

SYSTEM_PROMPT = f"""You are the AI content strategist for Shekhar Shrestha (@marketing.shekhar), Instagram Growth Strategist at Orcalynx Agency.

You have two jobs today:
1. DECIDE what carousel topic will perform best for Shekhar's audience RIGHT NOW — based on real research data provided to you, trends, and deep knowledge of what service-based business owners on Instagram need.
2. BUILD a complete, polished carousel HTML using the exact design system provided.

{BRAND_VOICE}

{DESIGN_SYSTEM}

The full CSS is already written for you — you just need to write the HTML body with the slide divs. The CSS classes are all defined above.
Output ONLY the complete HTML file. No explanation, no markdown, no ```html fences. Start with <!DOCTYPE html> and end with </html>.
"""

USER_PROMPT = f"""Today is {DAY_NAME}, {TODAY}. This is the {session_label} carousel run.

## RESEARCH DATA (from live web search — use this to inform your topic decision)

{research_text}

## YOUR TASK

Step 1 — THINK DEEPLY about what to create:
- What is the single most relevant, timely topic for service-based business owners on Instagram RIGHT NOW?
- What pain are they feeling this week? What question are they Googling?
- What has NOT been overdone in Shekhar's content style recently?
- The topic must be actionable, specific, and directly serve coaches/consultants/agency owners
- Draw from the research data above AND your deep knowledge of Instagram strategy trends

Step 2 — DECIDE the topic and pick a hook formula from the brand voice guide

Step 3 — BUILD the complete carousel HTML:
- 6–8 slides
- carousel-light format (warm paper cream #F2EADB background)
- Use the exact CSS classes defined in the design system
- Mix at least 3 different visual components (step cards, framework rows, 2x2 grid, contrast pair, big stat, weekly schedule)
- Never use the same component on back-to-back slides
- Cover: eyebrow badge + big h1 with one <em> amber word + sub line + swipe cue
- Body slides: chip (STEP 0N of 0N) + h2 with .hl highlight + lede + ONE component
- CTA final slide: badge + h2 with <em> word + actions block with comment keyword + follow bar
- No handle or pagination in slide footers
- Voice: "we"/"our clients", en dash –, specific numbers, no fluff, no paid ads

The full CSS to embed is:
{FULL_CSS}

Output only the complete HTML. Begin with <!DOCTYPE html>.
"""

payload = json.dumps({{
    "model": "claude-opus-4-5",
    "max_tokens": 16000,
    "system": SYSTEM_PROMPT,
    "messages": [{{"role": "user", "content": USER_PROMPT}}]
}}).encode()

req = urllib.request.Request(
    "https://api.anthropic.com/v1/messages",
    data=payload,
    headers={{
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }},
    method="POST"
)

resp = json.loads(urllib.request.urlopen(req, timeout=180).read())
html_content = resp["content"][0]["text"].strip()

# Clean up if model wrapped in fences
if html_content.startswith("```"):
    lines = html_content.split("\n")
    html_content = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

print(f"  Generated {len(html_content):,} chars of HTML")

# Save locally for debugging
with open("/tmp/carousel_output.html", "w") as f:
    f.write(html_content)

# ─────────────────────────────────────────────
# 4. DEPLOY TO VERCEL
# ─────────────────────────────────────────────

print("🚀 Deploying to Vercel...")

slug = TODAY.replace("-", "") + "-" + session_label
html_b64 = base64.b64encode(html_content.encode()).decode()

deploy_payload = json.dumps({{
    "name": "shekhar-carousels",
    "files": [{{"file": "index.html", "data": html_b64, "encoding": "base64"}}],
    "projectSettings": {{"framework": None, "outputDirectory": "."}},
    "target": "production"
}}).encode()

deploy_req = urllib.request.Request(
    "https://api.vercel.com/v13/deployments?teamId=shekharrshresthaa-9402",
    data=deploy_payload,
    headers={{
        "Authorization": f"Bearer {{VERCEL_TOKEN}}",
        "Content-Type": "application/json"
    }},
    method="POST"
)

deploy_resp = json.loads(urllib.request.urlopen(deploy_req, timeout=60).read())
url = deploy_resp.get("url", "")
deploy_id = deploy_resp.get("id", "")

print(f"""
✅ Carousel complete!
📌 Session: {{session_label}}
🗓 Date: {{TODAY}}
🔗 URL: https://{{url}}
🆔 Deploy ID: {{deploy_id}}
""")
