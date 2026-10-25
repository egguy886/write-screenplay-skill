# 写剧本 Skill（Write-Screenplay Skill）

[English](README.md) · **简体中文**

> **把小说、粗纲、世界观设定转成可直接投产的微短剧剧本——同时产出 AI 视频管线需要的资产圣经。**
> 面向竖屏短剧（ReelShort、DramaBox、ShortMax、TikTok、抖音、快手），并有专门的出海模式：英文角色名、给制作团队看的中文动作与镜头、地道美式英文对白 + 每句中文潜台词。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/Agent-Claude%20Code%20%7C%20Codex%20%7C%20Antigravity%20%7C%20Grok-orange.svg)](#安装)
[![AI Video](https://img.shields.io/badge/AI%20Video-MiniMax%20H3%20%7C%20Kling%20%7C%20Runway%20%7C%20Sora-brightgreen.svg)](#核心特性)

---

## 为什么要做这个

AI 短剧里，剧本是下游一切的地基：剧本里的每个人物、每套衣服、每件道具、每个场景，都是一张要生成、要锁定的参考图；每个有台词的角色，都是一条要选定的声线。剧本弱，要付两次代价：一次在成片里，一次在白白浪费的生成次数里。

本 skill 覆盖整个前期：

```
小说/粗纲 ──► 长篇压缩 ──► 带集尾钩子的分集大纲 ──► 逐集剧本 ──► 制作圣经 ──► AI 视频管线
            （≤60 集）   （钩子轮换、付费墙、中点）   （自动检查） （人物/造型/道具/场景/声线） （资产库 + 参考图提示词）
```

## 核心特性

- 🎭 **双模式写作**
  - **国内中文短剧**：中文人名、动作、台词，适配抖音/快手节奏（黄金 3 秒、30 秒加压、60 秒爽点、硬断章）。
  - **出海微短剧**：强制英文角色名，场景与动作用中文（方便国内团队），对白为地道美式英语，每句附中文潜台词。
- 📚 **长篇改编模式**：把上百章的长篇压进固定集数（默认 ≤60）：章节节拍卡 → 压缩决策 → 加权集数预算 → 分集大纲 → 分批写作 → 连续性账本，每一步都有门禁和检查脚本。
- 🪝 **集尾钩子系统**：八种钩子、三档强度与"钩子阶梯"、前 10 秒必须回钩、题材钩子库（含言情类非暴力钩子），自动检查轮换。
- 🧬 **制作圣经**：人物四层档案（戏剧/语言/视觉/声音）、按阶段设计的造型（换装 = 新资产 ID）、道具生命周期、场景、声线，统一在一份 `bible.json`。逐集交叉核对剧本，生成带生图优先级的分集资产表，并导出 AI 视频管线的资产库与参考图提示词。
- ✍️ **人物与对白**：欲望/需要/错误信念、压力下的选择、语言档案（"这个人绝不会说什么"）、潜台词、四种信息工具（悬疑、惊奇、戏剧反讽、悬念），压缩到 2 分钟一集的用法。
- 🎬 **AI 视频友好的动作解耦**：一个微镜头一个主动量，动作有"起—做—收"，明确画左/画右，避免扩散模型融化肢体、人物漂移。

## 目录结构

```text
write-screenplay-skill/
├── SKILL.md                              # Skill 定义（给 Agent 看，中文）
├── README.md / README.zh-CN.md           # 英文 / 中文说明页
├── templates/
│   ├── chinese_script_template.md        # 国内中文剧本模板
│   ├── overseas_script_template.md       # 出海剧本模板
│   └── adaptation/                       # 长篇模式：改编参数、压缩决策、连续性账本、分集大纲示例、单集模板、制作圣经示例
├── references/
│   ├── novel-to-script-engine.md         # 小说因果剥离与内心外化
│   ├── overseas-script-protocol.md       # 出海题材与对白规范
│   ├── ai-friendly-beat-decoupling.md    # AI 视频动作解耦
│   ├── long-novel-adaptation.md          # 压缩工具箱、集数预算、分集卡片
│   ├── episode-hook-system.md            # 八种钩子、钩子阶梯、回钩
│   ├── character-and-dialogue.md         # 人物设计、语言档案、潜台词、信息工具
│   └── production-bible.md               # 人物/造型/道具/场景/声线，ID 规则，导出
└── scripts/                              # 零依赖 Python 3 工具
    ├── install.py                        # 一键链接到各 Agent
    ├── chapter_index.py                  # 扫章节 → 节拍卡骨架（字数、对白/短信占比、章尾）
    ├── merge_cards.py                    # 分卷节拍卡合并
    ├── episode_budget.py                 # 按卷加权分配集数；查付费墙/中点/高潮
    ├── outline_check.py                  # 大纲门禁：章节覆盖、钩子轮换、钩子阶梯、付费墙
    ├── script_lint.py                    # 单集门禁：格式、对白预算、时长估算、心理描写、集尾钩子
    ├── bible_check.py                    # 圣经门禁、剧本交叉核对、分集资产表、管线导出
    └── adapt_common.py
```

## 安装

**方式一：一次链接到所有 Agent**

```bash
git clone https://github.com/egguy886/write-screenplay-skill.git
cd write-screenplay-skill
python scripts/install.py
```

会链接到 `~/.claude/skills/`（Claude Code）、`~/.codex/skills/`（Codex CLI）、`~/.gemini/config/skills/`（Antigravity）、`~/.agents/skills/`（其他 Agent）。

**方式二：放进单个项目**

```bash
git clone https://github.com/egguy886/write-screenplay-skill.git .agents/skills/write-screenplay
```

## 使用

用名字或触发词调用：`/写剧本`、`写剧本`、`小说转剧本`、`出海剧本`、`长篇改编`、`分集大纲`、`制作圣经`、`人物小传`、`screenplay`、`novel-to-script`。

**示例**

```text
把这部小说第一章改成 3 集国内竖屏短剧，每集 90 秒，突出身份逆转的爽点。

把附带的世界观改成出海短剧（ReelShort 风格）：英文角色名、中文动作、英文对白加中文潜台词。

我的小说有 138 章，压成 60 集、每集 2 分钟的短剧。先做节拍卡和分集大纲。

给主要角色建制作圣经，并导出给我的 AI 视频管线。
```

### 长篇模式一览

| 步 | 产物 | 工具 | 门禁 |
| :--- | :--- | :--- | :--- |
| L0 立项参数 | 集数上限、时长、平台、尺度、画外音、红线 | 模板 | 用户确认 |
| L1 全书消化 | `chapters.json` 节拍卡 | `chapter_index.py`、`merge_cards.py` | 每章有卡；**章尾已核对正文** |
| L2 压缩决策 | 支线、角色、场景、重复桥段、重排 | 模板 | 每项有结论和理由 |
| L2.5 制作圣经 | `bible.json` | `bible_check.py` | 无 ❌；主角人设用户确认 |
| L3 集数预算 | 每卷集数 | `episode_budget.py` | 总数 ≤ 上限 |
| L4 分集大纲 | `episodes.json` → 可读大纲 | `outline_check.py` | 无 ❌；**用户逐集审过** |
| L5 逐集写作 | 剧本，每批 5 集 | `script_lint.py`、`bible_check.py --scripts` | 无 ❌ |
| L6 连续性账本 | 账本，每卷通读 | 模板 | 账本与剧本一致 |

### 输出格式（出海模式）

```markdown
### 场 01. The Aurelian 18 楼门厅 · 内 · 清晨
**出场人物**：Wren, Lucien
**造型**：Wren=C01-SHARK, Lucien=C02-SUIT
**核心道具**：外卖咖啡、旧手绳

△ （中景）18A 的门无声滑开，Lucien 提着公文包走出。
△ （特写）Wren 脚上的鲨鱼拖鞋张着毛绒大嘴。

**Lucien**
（俯身，把咖啡递给她）
"Drink it quickly, little mouse."
（中文潜台词：别想躲，我们有很多账要算。）

**【Episode 009 完 · 集尾钩子：line】**
```

场次标题用 `### 场 NN.`、说话人用 `**Name**`，下游台词锁定工具可以直接读取。画外音（`**Name (V.O.)**`）和屏幕文字（`【屏幕 · A → B】`）不进视频模型，后期配音/叠字。

## 质量门禁

每份剧本交付前检查：

1. **命名**：出海剧本只用英文角色名。
2. **解耦**：一个动作句不超过两个复合动作。
3. **纯视觉**：没有拍不出来的心理描写，全部外化。
4. **三秒抓人**：第 1 集前 3 秒必须抓人。
5. **断章**：每集停在答案出口前的那一刻。
6. **双语**：每句英文台词都有中文潜台词。
7. **回钩**（长篇模式）：前 10 秒接住上一集的钩子。
8. **预算**（长篇模式）：对白 + 画外音在预算内（2 分钟约 220 词）；≤4 场。
9. **账本**（长篇模式）：信息差、道具、关系与账本一致。
10. **人设**：每个说话人符合语言档案；主角本集做了一个有代价的选择。
11. **资产**：人物、造型、关键道具、场景都在圣经里。

## 相关项目

- [jtydhr88/screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills)：MIT 开源的深度编剧理论库（结构、人物、对白、连续剧写作，提炼自 47 本编剧书）。它不针对微短剧；需要底层理论时，可把其中的 `sw-character-conflict`、`sw-dialogue`、`sw-series-structure` 与本 skill 搭配使用。

## 许可证

[MIT](LICENSE)。欢迎 Star、Fork 和 PR。
