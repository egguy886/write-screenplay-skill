# Write-Screenplay Skill

**English** · [简体中文](README.zh-CN.md)

> **An agent skill that turns novels, outlines and world-building into production-ready micro-drama screenplays — and the asset bible your AI video pipeline needs.**
> Built for vertical short drama (ReelShort, DramaBox, ShortMax, TikTok, Douyin, Kuaishou), with a dedicated overseas mode: English character names, Chinese action and camera lines for the production team, and natural American English dialogue with Chinese subtext notes.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/Agent-Claude%20Code%20%7C%20Codex%20%7C%20Antigravity%20%7C%20Grok-orange.svg)](#installation)
[![AI Video](https://img.shields.io/badge/AI%20Video-MiniMax%20H3%20%7C%20Kling%20%7C%20Runway%20%7C%20Sora-brightgreen.svg)](#features)

---

## Why this exists

In AI short-drama production, the screenplay is the foundation of everything downstream. Every character, every outfit, every prop and every location in the script becomes a reference image that has to be generated and locked; every speaking role becomes a voice that has to be cast. A weak script costs you twice: once on screen, and again in wasted generations.

This skill covers the whole front end:

```
Novel / outline ──► Long-novel compression ──► Episode outline with cliffhangers ──► Scripts ──► Production bible ──► AI video pipeline
                    (≤60 episodes)              (hook rotation, paywall, midpoint)    (lint)     (characters, wardrobe,   (asset library +
                                                                                                   props, locations, voices) reference-image prompts)
```

## Features

- 🎭 **Two writing modes**
  - **Domestic Chinese** — Chinese names, action and dialogue, tuned to Douyin / Kuaishou pacing (3-second hook, 30-second escalation, 60-second payoff, hard cliffhanger).
  - **Overseas micro-drama** — English character names (enforced), Chinese sluglines and action for the production crew, authentic American English dialogue, and a Chinese subtext line under every line of dialogue.
- 📚 **Long-novel mode** — compresses a 100+ chapter novel into a fixed episode count (default ≤60): chapter beat cards → compression decisions → weighted episode budget → episode outline → batch writing → continuity ledger. Every stage has a gate and a checker script.
- 🪝 **Cliffhanger system** — eight hook types, three hook levels with a "hook ladder", a mandatory payoff of the previous hook in the first 10 seconds, genre hook libraries (including non-violent hooks for romance), and automatic rotation checks.
- 🧬 **Production bible** — four-layer character profiles (drama / voice / visual / casting), wardrobe by phase (a costume change is a new asset ID), prop lifecycles, locations and voices in one `bible.json`. It cross-checks every script, produces a per-episode asset breakdown with generation priority, and exports an asset library plus reference-image prompts for an AI video pipeline.
- ✍️ **Character & dialogue craft** — want / need / misbelief, choices under pressure, voice sheets ("what this character never says"), subtext, and the four information tools (mystery, surprise, dramatic irony, suspense) — condensed for two-minute episodes.
- 🎬 **AI-video-ready action decoupling** — one momentum per micro-shot, open → execute → close for every action, explicit screen-left / screen-right, so diffusion video models don't melt limbs or drift.

## Directory structure

```text
write-screenplay-skill/
├── SKILL.md                              # Skill definition (agent-facing, Chinese)
├── README.md / README.zh-CN.md           # This page, in English and Chinese
├── templates/
│   ├── chinese_script_template.md        # Domestic Chinese script template
│   ├── overseas_script_template.md       # Overseas script template
│   └── adaptation/                       # Long-novel mode: parameters, compression decisions, continuity ledger,
│                                         #   episode outline example, episode template, production bible example
├── references/
│   ├── novel-to-script-engine.md         # Novel → script: causal skeleton, externalising interiority
│   ├── overseas-script-protocol.md       # Overseas genres and dialogue rules
│   ├── ai-friendly-beat-decoupling.md    # Action decoupling for AI video
│   ├── long-novel-adaptation.md          # Compression toolbox, episode budget, outline cards
│   ├── episode-hook-system.md            # Eight hook types, hook ladder, open-payoff
│   ├── character-and-dialogue.md         # Character design, voice sheets, subtext, information tools
│   └── production-bible.md               # Characters, wardrobe, props, locations, voices; ID rules; export
└── scripts/                              # Zero-dependency Python 3 tools
    ├── install.py                        # Link the skill into every supported agent
    ├── chapter_index.py                  # Scan chapters → beat-card skeleton (word count, dialogue/text-message share, chapter endings)
    ├── merge_cards.py                    # Merge beat cards written volume by volume
    ├── episode_budget.py                 # Weighted episode allocation per arc; paywall / midpoint / climax checks
    ├── outline_check.py                  # Outline gate: chapter coverage, hook rotation, hook ladder, paywall
    ├── script_lint.py                    # Episode gate: format, dialogue budget, runtime estimate, interiority, ending hook
    ├── bible_check.py                    # Production bible gate, script cross-check, asset breakdown, pipeline export
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

Trigger it by name or with any of: `/写剧本`, `screenplay`, `novel-to-script`, `production bible`, `character bible`, `long-novel adaptation`.

**Examples**

```text
Adapt chapter 1 of this novel into three 90-second domestic vertical episodes. Lean on the identity-reversal payoff.

Turn this world-building doc into an overseas micro-drama (ReelShort style): English names, Chinese action, English dialogue with Chinese subtext.

My novel has 138 chapters. Compress it into a 60-episode, 2-minute-per-episode drama. Start with the beat cards and the episode outline.

Build the production bible for the main cast and export it for my AI video pipeline.
```

### Long-novel mode at a glance

| Step | Output | Tool | Gate |
| :--- | :--- | :--- | :--- |
| L0 Parameters | episode cap, runtime, platform, content level, voice-over policy, red lines | template | user confirms |
| L1 Digest | `chapters.json` beat cards | `chapter_index.py`, `merge_cards.py` | every chapter carded; **endings checked against the actual text** |
| L2 Compression | subplots, characters, locations, repeated beats, reordering | template | every item has a decision and a reason |
| L2.5 Production bible | `bible.json` | `bible_check.py` | no ❌; leads approved by the user |
| L3 Budget | episodes per arc | `episode_budget.py` | total ≤ cap |
| L4 Outline | `episodes.json` → readable outline | `outline_check.py` | no ❌; **user reviews every episode** |
| L5 Writing | scripts, 5 episodes per batch | `script_lint.py`, `bible_check.py --scripts` | no ❌ |
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

Scene headings use `### 场 NN.` and speakers use `**Name**`, so scripts load directly into downstream dialogue-locking tools. Voice-over (`**Name (V.O.)**`) and on-screen text (`【屏幕 · A → B】`) are kept out of the video model and added in post.

## Quality gates

Every script is checked before delivery:

1. **Naming** — overseas scripts use English character names only.
2. **Decoupling** — no action line carries more than two compound movements.
3. **Visual only** — no unfilmable interior monologue; externalise it.
4. **Three-second hook** — episode 1 grabs in the first three seconds.
5. **Cliffhanger** — every episode ends on the moment before the answer lands.
6. **Bilingual** — every English line has a Chinese subtext note.
7. **Open-payoff** *(long mode)* — the first 10 seconds pay off the previous hook.
8. **Budget** *(long mode)* — dialogue + V.O. within budget (~220 words per 2 minutes); ≤4 scenes.
9. **Continuity** *(long mode)* — information state, props and relationship match the ledger.
10. **Character** — every speaker matches their voice sheet; the lead makes a costly choice.
11. **Assets** — every character, outfit, key prop and location exists in the bible.

## Related

- [jtydhr88/screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills) — a deep, MIT-licensed screenwriting craft library (structure, character, dialogue, series writing, distilled from 47 craft books). It is not micro-drama specific; pair `sw-character-conflict`, `sw-dialogue` and `sw-series-structure` with this skill when you want the underlying theory.

## License

[MIT](LICENSE). Stars, forks and pull requests are welcome.
