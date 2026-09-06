# 写剧本 Skill (Write-Screenplay Skill)

> **工业级小说/设定转剧本智能体工作流（Novel & Lore to Screenplay Engine）**  
> 一键将小说原著、粗纲设定、脑洞小传转化为专业商业剧本，支持**国内中文短剧**与**出海短剧（英文角色名+中文动作+地道英文对白）**双模式，全面适配各大 AI Agent 平台、海内外短剧分发平台与下游 AI 视频生成大模型。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform: Claude Code / Codex / Antigravity / Grok](https://img.shields.io/badge/Agent-Claude%20%7C%20Codex%20%7C%20Antigravity%20%7C%20Grok-orange.svg)](#平台适配)
[![Video Engine: MiniMax H3 / Kling / Sora](https://img.shields.io/badge/AI%20Video-MiniMax%20%7C%20Kling%20%7C%20Runway-brightgreen.svg)](#ai-视频友好型动作解耦)

---

## 🌟 核心特性 (Key Features)

- 🎭 **双模式智能创作引擎 (Dual-Mode Scriptwriting Engine)**
  - **国内中文短剧模式**：全中文角色名、全中文动作与台词。精准适配抖音、快手、微信小程序、爱优腾微短剧的“黄金三秒开头”、“30秒情绪反转”、“60秒爆爽打脸”与“集尾致命钩子（Cliffhanger）”。
  - **出海短剧模式 (Overseas Micro-Drama)**：**【核心铁律】角色名全量使用英文（如 `Lucas`, `Grover`, `Kaiser`）**，动作描写、场景 Slugline、运镜指示保持**全中文**（便于国内制作人/导演把控视听语言与调度），对白采用**地道高冲击力美语**，并附带**中文潜台词与情绪意图**。
- ✂️ **小说因果骨架剥离引擎 (Deconstruction Engine)**
  - 自动剥离小说中无法拍摄的大段心理描写、作者全知全能叙事与静态抒情。
  - 将抽象情绪“攥取外化”为演员可执行的物理动作与镜头画面。
- 🎬 **AI 视频生成友好型动作解耦 (Prompt-Ready Action Decoupling)**
  - 针对 MiniMax H3、Kling、Runway Gen-3、Sora 等视频扩散模型的生成特性，强制拆解复杂多动量动作为“单动量原子微节拍”，彻底杜绝长句动作引起的肢体融化、多头多手和模型幻觉。
- 🌐 **全主流平台适配 (Universal Compatibility)**
  - **AI 智能体平台**：Claude Code (`~/.claude/skills`)、Codex (`~/.codex/skills`)、Google Antigravity (`.agents/skills` / `.gemini/config/skills`)、xAI Grok (`~/.grok/skills`)、豆包等。
  - **分发平台**：国内（抖音、快手、腾讯微短剧、微信小程序），出海（ReelShort, DramaBox, ShortMax, FlexTV, TikTok）。

---

## 📂 目录结构 (Directory Structure)

```text
写剧本-skill/
├── SKILL.md                              # 核心 Skill 定义与运行规范
├── README.md                             # 仓库中英文使用指南
├── LICENSE                               # 开源协议 (MIT)
├── templates/                            # 标准剧本输出模板
│   ├── chinese_script_template.md        # 国内中文短剧剧本模板
│   └── overseas_script_template.md       # 出海短剧剧本模板（英文名+中文动作+英文对白）
├── references/                           # 深度工作流参考规范
│   ├── novel-to-script-engine.md         # 小说因果剥离与戏剧化重构法
│   ├── overseas-script-protocol.md       # 出海短剧主流题材与对白规范
│   └── ai-friendly-beat-decoupling.md    # AI 视频动作解耦与防融化规范
└── scripts/
    └── install.py                        # 一键软链/安装到各大 Agent 平台的脚本
```

---

## 🚀 安装与部署 (Installation)

### 方式 1：使用 Python 脚本一键安装到所有 Agent
本项目内置跨平台安装脚本，可自动检测并软链到本地所有的 Agent 根目录：

```bash
python scripts/install.py
```
> 支持自动桥接到：
> - `~/.agents/skills/write-screenplay` (通用 Agent / 豆包 / Trae Solo)
> - `~/.claude/skills/write-screenplay` (Claude Code)
> - `~/.codex/skills/write-screenplay` (Codex CLI)
> - `~/.gemini/config/skills/write-screenplay` (Google Antigravity IDE)

### 方式 2：Git 克隆
可以直接克隆到当前工程的 `.agents/skills/` 目录下：
```bash
git clone https://github.com/egguy886/write-screenplay-skill.git .agents/skills/write-screenplay
```

---

## 💡 触发词与调用方式 (Usage)

在任何支持 Skill 规范的 Agent（如 Antigravity / Claude Code / Codex / Grok）中，直接输入以下指令即可激活：

```text
/写剧本
写剧本
小说转剧本
改编剧本
出海剧本
短剧剧本
screenplay
novel-to-script
```

### 常用指令示例：
1. **中文短剧改编**：
   > “请使用【写剧本 skill】将以下小说第一章改编成 3 集国内中文竖屏短剧，每集 90 秒，突出主角身份逆转的爽点。”
2. **出海短剧改编**：
   > “请使用【写剧本 skill】把附带的世界观设定改编为一部出海短剧（ReelShort 风格），采用出海模式：角色名为英文，动作与镜头为中文，对白为英文加中文潜台词。”

---

## 📑 双模式格式对比 (Format Comparison)

### 1. 国内中文剧本范式
```markdown
### 场 01. 第九机甲维修区 · 露天工坊 · 夜（暴雨）
**出场人物**：林辰、赵工头  
**核心道具**：生锈扳手、黄铜传动轴  

△ （全景）暴雨倾盆。蒸汽管道喷吐滚烫白烟。
△ （中景）林辰跪在泥浆中，双手用力旋紧底盘螺栓。
△ （特写）工头赵大彪厚重的铁头皮靴暴力踹在林辰背上！

赵工头
（居高临下，啐了一口唾沫）
“动作慢得像条死狗！今天修不好，一分钱工钱别想拿！”
```

### 2. 出海剧本范式 (Overseas Standard)
```markdown
### Scene 01. Sector Nine Mecha Repair Bay · Open Yard · Night (Heavy Rain)
**Characters**: Lucas, Grover  
**Key Props**: Heavy iron ratchet wrench, brass transmission shaft  

△ （全景）暴雨如注，黑夜浓稠如机油。蒸汽排气阀嘶嘶喷吐滚烫白雾。
△ （中景）Lucas 全身湿透，单膝跪在泥浆里拧紧最后一枚轴承螺母。
△ （特写）靴底破空声炸响！工头 Grover 狞笑着抬起铁头军靴，狠狠踹中 Lucas 后背！

Grover
（居高临下狞笑，向泥浆吐出黑色烟草汁）
"Moving slow as a dead dog! Tune this rig tonight, or you won't even have mud water to drink!"
（中文潜台词：动作慢得像条死狗！今晚修不好这破机甲，你连泥水都没得喝！）

Lucas
（侧脸紧贴湿泥，双目如铁，咬牙从牙缝挤出）
"Drive shaft is fixed. My wages."
（中文潜台词：传动轴修好了。我的工钱。）
```

---

## 🛡️ 生成前 6 项工业门禁 (Pre-Output Quality Gate)

每次生成剧本前，智能体必须严格执行以下六重门禁审查：
1. **[角色命名门禁]** 出海剧本角色名 100% 为合规英文命名，杜绝汉字人名。
2. **[动作解耦门禁]** 单个动作句绝不塞入超过 2 个复合大动作，保持单动量原子化。
3. **[纯视觉化门禁]** 切除所有不可视心理描写，转译为动作白描。
4. **[三秒抓人门禁]** 首集前 3 秒具备极限悬念或强视听压迫。
5. **[集尾断章门禁]** 结尾必须断在危机高潮，绝不拖泥带水平淡收场。
6. **[双语对照门禁]** 出海剧本英文台词全部附带传神到位的中文意图与潜台词。

---

## 📄 开源许可证 (License)

本项目基于 [MIT License](LICENSE) 开源。欢迎 Star、Fork 并提交 PR！
