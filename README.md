# Write-Screenplay Skill (v4.2)

**English** · [简体中文](README.zh-CN.md)

> **An agent skill that turns novels, outlines and world-building into production-ready commercial screenplays — combining theatrical cinematic breathing room with addictive episode cliffhangers, plus the asset bible your AI video pipeline needs.**
> Supports **user-selectable widescreen cinema (`16:9` / `2.39:1`) and vertical fast-paced micro-drama (`9:16`)**, story-and-audiovisual-first **elastic runtimes without rigid duration caps**, Domestic Chinese scripts, and Overseas scripts (English character names, Chinese director action/camera cues, authentic American English dialogue + Chinese subtext notes).

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/Agent-Claude%20Code%20%7C%20Codex%20%7C%20Antigravity%20%7C%20Grok-orange.svg)](#installation)
[![AI Video](https://img.shields.io/badge/AI%20Video-MiniMax%20H3%20%7C%20Kling%20%7C%20Runway%20%7C%20Sora-brightgreen.svg)](#features)

---

## Why this exists

In commercial series and AI cinema/short-drama production, the screenplay is the foundation of everything downstream. Every character, every outfit, every prop and every location in the script becomes a reference image that has to be generated and locked; every speaking role becomes a voice that has to be cast. A weak script costs you twice: once on screen, and again in wasted generations.

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
  - **Overseas (`--mode overseas`)** — English character names (enforced), Chinese sluglines and action for the directing/storyboarding crew, authentic American English dialogue, and a non-literal Chinese subtext line under every line of dialogue.
- 📚 **Long-novel mode (compression or 1:1 chapter-to-episode)** — chapter beat cards → adaptation decisions → episode budget → episode outline → batch writing → continuity ledger. Every stage has a gate and a checker script.
- 🪝 **Cliffhanger system** — eight hook types, three hook levels with a "hook ladder", a mandatory payoff of the previous hook in the opening seconds, genre hook libraries, and automatic rotation checks.
- 🧬 **Production bible** — four-layer character profiles (drama / voice / visual / casting), wardrobe by phase, prop lifecycles, locations and voices in `bible.json`, exporting directly to AI video pipelines (`--export-h3`).
- 🎬 **AI-video-ready action decoupling** — one momentum per micro-shot, step-by-step physical causality, explicit screen-left / screen-right anchors.

## Installation

```bash
git clone https://github.com/egguy886/write-screenplay-skill.git
cd write-screenplay-skill
python scripts/install.py
```

## License

[MIT](LICENSE). Stars, forks and pull requests are welcome.
