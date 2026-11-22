# 写剧本 Skill（Write-Screenplay Skill v5.0）

[English](README.md) · **简体中文**

> **前制编导与空间站位一体的商业剧本引擎——把小说、粗纲、世界观设定转成“零空间穿帮、静音能看懂因果、直接喂给 AI 视频管线”的电影级剧本与制作圣经。**
> 吸收前制编导台（大纲节拍 / 静音可读动作流 / 开场站位锁）方法论：支持**横版电影大片（`16:9` / `2.39:1`）与竖版快节奏短剧（`9:16`）自由选择**，强制**“一子空间一场戏 + 每场内置开场站位锁 + 真实语速与动作节拍双轨定长 + 集尾强钩子”**；同时提供国内中文模式与出海模式（英文角色名、中文导演调度、地道美式英文对白 + 中文真潜台词）。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/Agent-Claude%20Code%20%7C%20Codex%20%7C%20Antigravity%20%7C%20Grok-orange.svg)](#安装)
[![AI Video](https://img.shields.io/badge/AI%20Video-MiniMax%20H3%20%7C%20Kling%20%7C%20Runway%20%7C%20Sora-brightgreen.svg)](#核心特性)

---

## 为什么要做这个

商业剧集与 AI 影视制作里，剧本是下游一切的地基：剧本里的每个人物、每套衣服、每件道具、每个场景，都是一张要生成、要锁定的参考图；每个有台词的角色，都是一条要选定的声线。剧本弱，要付两次代价：一次在成片里，一次在白白浪费的生成次数里。

本 skill 覆盖整个前期：

```
小说/粗纲 ──► 长篇拆解或 1:1 映射 ──► 带集尾钩子的分集大纲 ──► 逐集电影感剧本 ──► 制作圣经 ──► AI 视频管线
             （弹性集数与片长）       （钩子轮换、付费墙、中点）   （自动检查）     （人物/造型/道具/场景/声线） （资产库 + 参考图提示词）
```

## 核心特性（v4.2）

- 🎞️ **横版电影大片与竖版快节奏自由选择**
  - **横版电影大片模式（`16:9` / `2.39:1`）**：宽银幕空间构图、大场面奇观定场、光影声效留白与人物情绪呼吸，同时保留每集结尾的硬核悬念钩子（适配 B 站、腾讯/爱奇艺精品网剧、YouTube 剧场、院线感 AI 番剧与动态漫）。
  - **竖版快节奏短剧模式（`9:16`）**：纵深居中构图、中近景与眼神特写主导、第一秒进事件、密集推拉与强断点（适配抖音、红果、快手、ReelShort、DramaBox）。
- ⏱️ **剧情与视听第一、弹性片长零死限**：不再机械卡死 90 秒或 120 秒上限，时长完全服从本集戏剧交锋与视听呼吸（从 90 秒竖屏快切到 3–6 分钟以上的横屏精品单集皆可），`script_lint.py` 自动按声明时长与画幅线性伸缩场次与对白容量。
- 🎭 **中英双语模式**
  - **国内中文精品模式（`--mode cn`）**：全中文人名、电影命名运镜、物理动作白描、真潜台词对白。
  - **出海电影感模式（`--mode overseas`）**：强制英文角色名，场景与动作用中文（方便国内导演与分镜团队），对白为地道美式口语英文，每句附非直译中文真潜台词。
- 📚 **长篇改编全链路（支持压缩集数或 1:1 逐章转译）**：章节节拍卡 → 改编与外化决策 → 集数预算 → 分集大纲 → 分批写作 → 连续性账本，每一步都有门禁和检查脚本。
- 🪝 **集尾强钩子系统**：八种钩子、三档强度与“钩子阶梯”、前 10 秒必须回钩、题材钩子库（含言情类非暴力钩子），自动检查轮换——确保哪怕拍成电影级视听质感，每一集结尾照样逼观众点下一集。
- 🧬 **制作圣经**：人物四层档案（戏剧/语言/视觉/声音）、按阶段设计的造型（换装 = 新资产 ID）、道具生命周期、场景、声线，统一在一份 `bible.json`。逐集交叉核对剧本，生成带生图优先级的分集资产表，并导出 AI 视频管线的资产库与参考图提示词。
- 🎬 **AI 视频友好的动作解耦**：一个微镜头一个主动量，动作单步递进，明确画左/画右，避免扩散模型融化肢体、人物漂移。

## 目录结构

```text
write-screenplay-skill/
├── SKILL.md                              # Skill 定义（v4.2 全画幅电影视听编导一体版）
├── README.md / README.zh-CN.md           # 英文 / 中文说明页
├── templates/
│   ├── chinese_script_template.md        # 国内中文剧本模板
│   ├── overseas_script_template.md       # 出海剧本模板
│   └── adaptation/                       # 长篇模式：改编参数、压缩决策、连续性账本、分集大纲示例、单集模板、制作圣经示例
├── references/
│   ├── cinematic-director-craft.md       # 电影级编导一体与去 AI 味宪法
│   ├── genre-gates.md                    # 按题材选用的六大题材门禁
│   ├── viewer-first-script.md            # 观众先看懂规范（v2）
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
    ├── episode_budget.py                 # 按卷分配集数；查付费墙/中点/高潮
    ├── outline_check.py                  # 大纲门禁：章节覆盖、钩子轮换、钩子阶梯、付费墙
    ├── script_lint.py                    # 单集门禁（v4.2）：支持 --aspect 16:9|2.39:1|9:16 与弹性时长动态核验
    ├── viewer_test.py                    # 新观众盲测看懂打分脚本
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

用名字或触发词调用：`/写剧本`、`写剧本`、`小说转剧本`、`横屏短剧`、`精品网剧`、`电影感剧本`、`出海剧本`、`长篇改编`、`分集大纲`、`制作圣经`、`screenplay`、`novel-to-script`。

**示例**

```text
把这部仙侠小说按 16:9 横版电影大片质感逐章 1:1 改编为精品网剧剧本，单集不限死时长（约 3–4 分钟），兼顾中式志怪视听呼吸与集尾强悬念钩子。

把附带的世界观改成 9:16 出海短剧（ReelShort 风格）：英文角色名、中文动作、英文对白加中文真潜台词。

给主要角色建制作圣经，并导出给我的 AI 视频管线。
```

### 长篇模式一览

| 步 | 产物 | 工具 | 门禁 |
| :--- | :--- | :--- | :--- |
| L0 立项参数 | 语言模式、画幅（`16:9` 横屏 / `9:16` 竖屏）、集数策略、弹性时长、平台、尺度、红线 | 模板 | 用户确认 |
| L1 全书消化 | `chapters.json` 节拍卡 | `chapter_index.py`、`merge_cards.py` | 每章有卡；**章尾已核对正文** |
| L2 改编决策 | 支线取舍或 1:1 提纯、角色归并、心理外化与视听设计 | 模板 | 每项有结论和理由 |
| L2.5 制作圣经 | `bible.json` | `bible_check.py` | 无 ❌；主角人设用户确认 |
| L3 集数预算 | 每卷集数 | `episode_budget.py` | 总数符合立项设定 |
| L4 分集大纲 | `episodes.json` → 可读大纲 | `outline_check.py` | 无 ❌；**用户审过** |
| L5 逐集写作 | 剧本（支持横竖屏与弹性片长） | `script_lint.py`、`bible_check.py --scripts` | 无 ❌ |
| L6 连续性账本 | 账本，每卷通读 | 模板 | 账本与剧本一致 |

## 质量门禁（v5.0 三层十项）

**A. 通用门禁（所有画幅与题材必过）**
1. **命名**：出海剧本只用英文角色名；中文剧本统一中文角色名（lint ❌）。
2. **去说明书独白**：角色不对空气解说自己的状态（lint ⚠，通用句式，中英文都查）。
3. **去复述与捧哏**：不向在场的人复述大家都知道的事；反派不替主角喊“怎么可能”（lint ⚠）。
4. **真潜台词且不藏戏核**：中文潜台词写没说出口的话，且严禁把原著关键动机转折与跨场呼应仅塞进潜台词括号（lint ⚠）。
5. **遮名可读**：遮住说话人名字，仍能分出是谁在说。
6. **双轨真实估时与集尾强钩子并存**：按对白真实语速（中 3.8 字/s、英 2.5 词/s）+ 动作节拍（横屏 3.2s/拍、竖屏 2.5s/拍）诚实定长，集尾停在答案出口前；第 2 集起开场回钩承接。
7. **资产与账本**：人物、造型、道具、子空间场景、信息差与圣经和账本一致（`bible_check.py`）。
8. **看懂测试**：没读过小说的读者复述本集；单集低于 7 分，或同一疑问 ≥ 2 遍重复出现，就回去改（`viewer_test.py`）。
9. **子空间独立分场与开场站位锁（v5.0 新增）**：严禁“女囚室与隔壁木牢”式复合子空间场标（lint ❌）；每场头部内置 `**开场站位**` 写清隔断物与内外/左右/朝向（`--strict-staging` 可升为 ❌）。
10. **静音可读与道具来源守恒（v5.0 新增）**：姿态反转（如躺回装睡）前必有可见触发源；掏出关键道具必写明物理出处（lint ⚠）。

**B. 题材门禁（按题材与画幅选用，`references/genre-gates.md`）**：开场、先让观众站到主角这边、阻力方的理由、“为什么不直接……”、换地方怎么到、首集兑现。`script_lint.py --genre --aspect` 会按画幅与题材检查开场。

**C. 交给分镜**：一段一空间、一镜一动量、段缝顺接、每 15 秒段词数控制，由下游 `h3-drama-kit` 执行。

## 相关项目

- [h3-drama-kit](https://github.com/egguy886/h3-drama-kit)：下一步，把剧本做成 MiniMax H3 成片（资产、分镜提示词、自检、AutoDL 出片、看片、后期）。`bible_check.py --export-h3` 直接导出它的资产库格式。
- [jtydhr88/screenwriting-skills](https://github.com/jtydhr88/screenwriting-skills)：MIT 开源的深度编剧理论库（结构、人物、对白、连续剧写作，提炼自 47 本编剧书）。

## 许可证

[MIT](LICENSE)。欢迎 Star、Fork 和 PR。
