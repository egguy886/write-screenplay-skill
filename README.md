# Write-Screenplay Skill (v5.0)

**English** · [简体中文](README.zh-CN.md)

> **A pre-production showrunner & spatial-staging screenplay skill that turns novels, outlines and world-building into zero-continuity-bug commercial scripts — pairing theatrical cinematic breathing room with addictive cliffhangers and an AI-ready production bible.**
> Internalizes pre-production staging gates (**one physical sub-space per scene + mandatory `**开场站位**` opening blocking + silent-readable action causality + deterministic speech/action runtime estimation**), supporting **widescreen cinema (`16:9` / `2.39:1`) and vertical micro-drama (`9:16`)**, Domestic Chinese scripts, and Overseas scripts.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/Agent-Claude%20Code%20%7C%20Codex%20%7C%20Antigravity%20%7C%20Grok-orange.svg)](#installation)
[![AI Video](https://img.shields.io/badge/AI%20Video-MiniMax%20H3%20%7C%20Kling%20%7C%20Runway%20%7C%20Sora-brightgreen.svg)](#features-v42)

---

## Why this exists

In commercial series and AI short-drama/cinema production, the screenplay is the foundation of everything downstream. Every character, every outfit, every prop and every location in the script becomes a reference image that has to be generated and locked; every speaking role becomes a voice that has to be cast. A weak script costs you twice: once on screen, and again in wasted generations.

This skill covers the whole front end:

```
Novel / outline ──► Compression or 1:1 mapping ──► Episode outline with cliffhangers ──► Cinematic scripts ──► Production bible ──► AI video pipeline
                    (flexible episode count)       (hook rotation, paywall, midpoint)    (v4.2 lint)          (characters, wardrobe,   (asset library +
                                                                                                               props, locations, voices) reference-image prompts)
```

## Features (v4.2)

- 🎞️ **User-selectable Aspect Ratio & Visual Grammar (`16:9` / `2.39:1` Widescreen Cinema vs. `9:16` Vertical)**
  - **Widescreen Cinematic Mode (`16:9` / `2.39:1`)** — built for Bilibili, Tencent/iQIYI boutique series, YouTube series, and cinematic AI animation/live-action: wide rule-of-thirds blocking, grand spectacle framing, atmospheric visual breathing room, **paired with hard serialized cliffhangers at every episode ending**.
  - **Vertical High-Density Mode (`9:16`)** — built for Douyin, Hongguo, ReelShort, DramaBox, ShortMax: tight center-framed close-ups, instant hook entry, rapid escalation, and sharp cliffhangers.
- ⏱️ **Story & Audiovisual First — Uncapped Elastic Duration** — no arbitrary 90s/120s ceiling; episode length scales naturally to serve dramatic weight and visual rhythm (from 90s vertical sprints to 3–6+ minute widescreen episodes), with `script_lint.py` dynamically scaling scene and dialogue budgets from declared duration and aspect ratio.
- 🎭 **Two language modes**
  - **Domestic Chinese (`--mode cn`)** — Chinese names, cinematic camera/action blocking, and crisp spoken Chinese dialogue with subtext.
  - **Overseas (`--mode overseas`)** — English character names (enforced), Chinese sluglines and action for the production crew, authentic American English dialogue, and a Chinese subtext line under every line of dialogue.
- 📚 **Long-novel mode (compression or 1:1 chapter-to-episode)** — compresses a 100+ chapter novel into a target episode count or maps chapters 1:1: chapter beat cards → adaptation decisions → episode budget → episode outline → batch writing → continuity ledger. Every stage has a gate and a checker script.
- 🪝 **Cliffhanger system** — eight hook types, three hook levels with a "hook ladder", a mandatory payoff of the previous hook in the first 10 seconds, genre hook libraries (including non-violent hooks for romance), and automatic rotation checks.
- 🧬 **Production bible** — four-layer character profiles (drama / voice / visual / casting), wardrobe by phase (a costume change is a new asset ID), prop lifecycles, locations and voices in one `bible.json`. It cross-checks every script, produces a per-episode asset breakdown with generation priority, and exports an asset library plus reference-image prompts for an AI video pipeline.
- ✍️ **Character & dialogue craft** — want / need / misbelief, choices under pressure, voice sheets ("what this character never says"), subtext, and the four information tools (mystery, surprise, dramatic irony, suspense).
- 🎬 **AI-video-ready action decoupling** — one momentum per micro-shot, open → execute → close for every action, explicit screen-left / screen-right, so diffusion video models don't melt limbs or drift.

## Directory structure

```text
write-screenplay-skill/
├── SKILL.md                              # Skill definition (v4.2 multi-aspect cinematic edition)
├── README.md / README.zh-CN.md           # This page, in English and Chinese
├── templates/
│   ├── chinese_script_template.md        # Domestic Chinese script template
│   ├── overseas_script_template.md       # Overseas script template
│   └── adaptation/                       # Long-novel mode: parameters, decisions, continuity ledger,
│                                         #   episode outline example, episode template, production bible example
├── references/
│   ├── cinematic-director-craft.md       # Cinematic showrunner & anti-AI dialogue craft
│   ├── genre-gates.md                    # Genre-specific gates (G1-G6)
│   ├── viewer-first-script.md            # Viewer comprehension spec (v2)
│   ├── novel-to-script-engine.md         # Novel → script: causal skeleton, externalising interiority
│   ├── overseas-script-protocol.md       # Overseas genres and dialogue rules
│   ├── ai-friendly-beat-decoupling.md    # Action decoupling for AI video
│   ├── long-novel-adaptation.md          # Compression toolbox, episode budget, outline cards
│   ├── episode-hook-system.md            # Eight hook types, hook ladder, open-payoff
│   ├── character-and-dialogue.md         # Character design, voice sheets, subtext, information tools
│   └── production-bible.md               # Characters, wardrobe, props, locations, voices; ID rules; export
└── scripts/                              # Zero-dependency Python 3 tools
    ├── install.py                        # Link the skill into every supported agent
    ├── chapter_index.py                  # Scan chapters → beat-card skeleton
    ├── merge_cards.py                    # Merge beat cards written volume by volume
    ├── episode_budget.py                 # Weighted or fixed episode allocation per arc
    ├── outline_check.py                  # Outline gate: chapter coverage, hook rotation, hook ladder, paywall
    ├── script_lint.py                    # Episode gate (v4.2): --aspect 16:9|2.39:1|9:16 & elastic duration
    ├── viewer_test.py                    # Blind viewer comprehension test
    ├── bible_check.py                    # Production bible gate, script cross-check, pipeline export
    └── adapt_common.py
```

## Installation

**Option 1 — link into every agent at once**

```bash
git clone https://github.com/egguy886/write-screenplay-skill.git
cd write-screenplay-skill
python scripts/install.py
```

The installer links the skill into `~/.claude/skills/` (Claude Code), `~/.codex/skills/` (Codex CLI), `~/.gemini/config/skills/` (Antigravity) and `~/.agents/skills/` (other agents).

**Option 2 — per project**

```bash
git clone https://github.com/egguy886/write-screenplay-skill.git .agents/skills/write-screenplay
```

## Usage

Trigger it by name or with any of: `/写剧本`, `screenplay`, `novel-to-script`, `widescreen series`, `production bible`, `character bible`, `long-novel adaptation`.

**Examples**

```text
Adapt this xianxia novel 1:1 into a 16:9 widescreen cinematic series (~3–4 min per episode, story-first elastic duration), pairing atmospheric visual breathing room with hard episode-ending cliffhangers.

Turn this world-building doc into a 9:16 overseas micro-drama (ReelShort style): English names, Chinese action, English dialogue with Chinese subtext.

Build the production bible for the main cast and export it for my AI video pipeline.
```

### Long-novel mode at a glance

| Step | Output | Tool | Gate |
| :--- | :--- | :--- | :--- |
| L0 Parameters | language mode, aspect ratio (`16:9` / `9:16`), episode strategy, elastic runtime, platform, red lines | template | user confirms |
| L1 Digest | `chapters.json` beat cards | `chapter_index.py`, `merge_cards.py` | every chapter carded; **endings checked against the actual text** |
| L2 Adaptation | subplots, characters, locations, visual breathing & externalisation | template | every item has a decision and a reason |
| L2.5 Production bible | `bible.json` | `bible_check.py` | no ❌; leads approved by the user |
| L3 Budget | episodes per arc | `episode_budget.py` | matches target scope |
| L4 Outline | `episodes.json` → readable outline | `outline_check.py` | no ❌; **user reviews** |
| L5 Writing | scripts (widescreen or vertical, elastic duration) | `script_lint.py`, `bible_check.py --scripts` | no ❌ |
| L6 Ledger | continuity ledger, per-volume read-through | template | ledger matches scripts |

### Output format (overseas mode)

```markdown
### 场 01. 私人俱乐部宴会厅 · 内 · 夜
**出场人物**：Ivy, Adrian
**造型**：Ivy=C01-GALA, Adrian=C02-SUIT
**核心道具**：旧钥匙扣

△ （中景）大厅门口，Adrian 停下脚步，视线越过人群，落在 Ivy 握杯的右手上。
△ （近景）Adrian 抬起右手，指间挂着一只旧钥匙扣。【停留 1.5 秒】

**Adrian**
（走到她面前，声音很轻）
"Careful. You're shaking."
（中文潜台词：别装了，我认得你。）

**【Episode 001 完 · 集尾钩子：reveal】**
```

## Quality gates (v5.0, three tiers)

**A. Universal — every script, every aspect ratio, every genre**
1. **Naming** — overseas scripts use English character names only; Chinese scripts keep unified Chinese names. *(lint ❌)*
2. **No self-narration** — characters never explain their own state to the air. *(lint ⚠, generic patterns, EN + CN)*
3. **No recap / no cheerleading** — nobody recaps what everyone in the room already knows; villains don't gasp "how is this possible". *(lint ⚠)*
4. **Real subtext without hiding plot beats** — subtext notes carry unspoken intent, never essential plot turns or cross-scene payoffs. *(lint ⚠)*
5. **Masked-name test** — cover the speaker names; you can still tell who is talking.
6. **Deterministic timing & cliffhanger coexistence** — honest runtime from true speech rate (3.8 CN chars/s, 2.5 EN words/s) + action beats (3.2s widescreen / 2.5s vertical), ending on a sharp cliffhanger.
7. **Assets & continuity** — characters, outfits, props, sub-space locations and information state match the bible and ledger. *(`bible_check.py`)*
8. **Viewer test** — a reader who never read the novel retells the episode; below 7/10 or a repeated confusion means rewrite. *(`viewer_test.py`)*
9. **One sub-space per scene & opening staging lock (v5.0)** — blocks composite multi-room sluglines *(lint ❌)* and checks per-scene `**开场站位**` spatial anchors *(`--strict-staging` promotes to ❌)*.
10. **Silent-readable causality & prop conservation (v5.0)** — flags posture reversals (e.g., feigning sleep) missing a visible external trigger and weapons/props drawn without a stated physical source. *(lint ⚠)*

**B. Genre gates — pick by genre & aspect ratio** (`references/genre-gates.md`): opening hook, siding with the lead, the opposition's reasons, "why don't they just…", how they got there, a first-episode payoff. `script_lint.py --genre --aspect` adapts opening checks to widescreen vs. vertical framing.

**C. Handed to storyboarding** — one space per 15-second segment, one movement per shot, matched cuts across segment seams, ≤ 26 words per segment. Executed downstream in `h3-drama-kit`.

## Related

- [h3-drama-kit](https://github.com/egguy886/h3-drama-kit) — turns these scripts into a finished AI series on MiniMax H3 (assets, shot prompts, linting, AutoDL generation, review, post). `bible_check.py --export-h3` writes its asset library format directly.
- [jtydhr88/screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) — a deep, MIT-licensed screenwriting craft library distilled from 47 craft books.

## License

[MIT](LICENSE). Stars, forks and pull requests are welcome.
