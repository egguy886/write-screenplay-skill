---
name: write-screenplay
description: |
  写剧本 skill：将小说或相关设定一键转译为专业级剧本（微短剧、影视、漫剧）。支持“国内中文剧本”与“出海短剧剧本（英文角色名+中文动作+英文对白）”双模式。深度适配主流平台（AI Agent平台：Claude Code、Codex、Antigravity、Grok、豆包；发行平台：抖音、快手、ReelShort、DramaBox、ShortMax、TikTok）。内置“AI视频生成友好型动作解耦”，解决复杂动作堆叠导致后续视频生成融化变形的核心痛点。
  内置“长篇改编模式”：把几十到上百章的长篇压进固定集数（默认 ≤60 集），先做章节节拍卡、压缩决策、集数预算、分集大纲（含开场回钩与集尾钩子），再逐集写作，并用脚本校验覆盖率、钩子轮换、对白预算和格式。
  内置“制作圣经”：人物四层档案（戏剧/语言/视觉/声音）、造型、道具生命周期、场景、声线一张总表，校验剧本一致性、生成分集资产表，并导出为 AI 视频管线（h3-drama-kit）的资产库与参考图提示词。
  EN: Novel/lore → professional micro-drama screenplays (Chinese or overseas English-dialogue mode), with long-novel compression to ≤60 episodes, cliffhanger system, production bible (characters, wardrobe, props, locations, voices) and AI-video-ready action decoupling.
  触发词：/写剧本、写剧本、小说转剧本、改编剧本、出海剧本、短剧剧本、剧本创作、长篇改编、分集大纲、压缩成60集、集尾钩子、人物小传、制作圣经、资产清单、screenplay、novel-to-script、production bible、character bible
---

# 写剧本 Skill (Novel & Worldbuilding to Screenplay Engine)

本 Skill 是将**小说原著、粗纲脑洞、人物小传或世界观设定集**，全流程转化为**高水准商业剧本（国内短剧 / 出海微短剧 / 影视电影 / 漫剧）**的工业级创作工作流。

---

## 一、 核心工作模式（Dual-Mode Engine）

在开始改编前，先明确用户的**输出模式**：

### 模式 A：国内中文短剧剧本（Domestic Chinese Script）
- **角色命名**：全中文角色名（如：林辰、陆天行、苏清雪）。
- **叙述语言**：全中文（场景、机位、动作、神态、潜台词、说话台词）。
- **戏剧核心**：契合国内抖音、快手、微信小程序、爱优腾横竖屏的强节奏叙事：
  - 黄金 3 秒强冲突开篇。
  - 第 30 秒情绪递进施压，第 60 秒强爽点/反转打脸。
  - 片尾精准断在悬念钩子（Cliffhanger Hook）。
- **台词风格**：短平快、高信息密度、强情绪煽动力。

### 模式 B：出海短剧剧本（Overseas Micro-Drama Script · 核心指定模式）
- **角色命名【强制铁律】**：**角色名全量使用英文（Character Name in English）**！
  - 示例：`Lucas`, `Grover`, `Kaiser`, `Lilian`, `Elara`, `Ethan`, `Chloe`。
  - 严禁在出海剧本中对角色名使用中文拼音或汉字。
- **动作与调度语言**：**场景 Slugline、动作描写、镜头机位、调度指令全量使用中文**！
  - 目的：便于国内导演、制作人、分镜师快速理解镜头因果与调度逻辑，无缝衔接后续 AI 分镜提示词编译器。
- **对白语言**：
  - **主对白**：标准地道美语对白（Authentic English Dialogue），严禁中式直译英语。
  - **中文潜台词/意图附注**：每句英文对白后必须附带括号中文潜台词与情绪意图，方便配音指导与国内监制审核。
  - 格式规范：
    ```text
    △ （特写）Lucas 被战靴死死踩在泥浆中，双目如铁，咬牙抬头。
    Lucas: "Drive shaft is fixed. My wages."
    （中文潜台词：传动轴已经修好了，把我的工钱结了。）
    ```
- **题材偏好与出海调优**：
  - 深度适配 ReelShort, DramaBox, ShortMax, FlexTV, TikTok。
  - 狼人与宿命伴侣（Werewolf & Luna/Alpha）、亿万富翁隐藏身份（Billionaire in Disguise）、豪门复仇与契约婚姻（Contract Marriage）、黑帮救赎（Mafia Romance）。

---

## 二、 小说转剧本的四步转译法（The 4-Step Pipeline）

### 第一步：因果骨架剥离（Deconstruction）
小说往往充斥大段心理独白、环境抒情与旁白解释，而**剧本只写摄影机能拍到的画面与收音器能录到的声音**：
1. **切除纯心理描写**：把“他心中充满了愤怒与屈辱” ➔ 转化为物理动作：“他指节捏得发白，指甲深深掐进掌心渗出血丝”。
2. **切除作者全知旁白**：把“这里是圣城最腐败的第九维修区，建立于三百年前……” ➔ 转化为镜头视觉：“生锈断裂的巨型蒸汽管道喷出滚烫白烟，废弃机甲残骸堆成三十米高的钢铁垃圾山”。
3. **提取每场戏剧动机（Goal - Obstacle - Stake）**：
   - 谁想要什么（Objective）？
   - 谁/什么在阻挡他（Conflict）？
   - 如果此时拿不到，将面临什么即刻代价（Urgency）？

### 第二步：节奏重构与短剧分集（Dramatization）
- 将小说松散的连续章节，重新切割成**标准化短剧单元**：
  - 单集时长：严格控制在 **60秒 ~ 120秒**。
  - 单集结构：
    - `00:00 - 00:05`：**黄金开场钩子**（视觉奇观、极端压迫或悬疑谜题）。
    - `00:05 - 00:45`：**对抗与行动推进**（人物为达成目的做出具体尝试，遭逢阻碍）。
    - `00:45 - 00:75`：**危机升级 / 绝地反击**（身份揭露、异能初醒或情势突变）。
    - `00:75 - 00:90/120`：**片尾断章钩子（Hook）**（危险迫近、枪口上膛、门被踹开，强制观众点击下一集）。

### 第三步：AI 视频生成友好型动作解耦（Prompt-Ready Decoupling）★★★
> [!IMPORTANT]
> **吸取 AI 视频生成的血泪教训：复杂的长句动作是扩散模型的毒药！**
> 如果剧本写：“主角一个翻滚避开子弹，顺势拔出匕首反手刺入敌人咽喉，随后借力后空翻稳稳落在车顶”，AI 视频模型在 5~15 秒内必然发生肢体融化、穿模、多头多手和严重漂移！

**本 Skill 强制执行“原子微节拍（Atomic Visual Beat）”原则**：
1. **一个微镜头只承载一个主力量动量**：
   - 动作 A：闪避扑地（单一跌落动量）
   - 动作 B：匕首刺击（单一向前穿透动量）
   - 动作 C：车顶站立定格（静态平衡姿态）
2. **动作必须有闭环（Open ➔ Execute ➔ Close）**：
   - 严禁模糊的动作半截悬空。拾取道具必须有“伸手 ➔ 抓取 ➔ 揣入口袋/握持”的完成态。
3. **空间站位与视线轴（180度法则）显式标记**：
   - 明确标出角色屏幕相对位置（screen-left / screen-right），杜绝镜头切换时两面人对撞漂移。

### 第四步：标准化剧本格式输出（Formatting）
严格采用电影工业标准排版：
- **场景标题（Slugline）**：`场景编号. 场景地点 · 空间属性 · 时间（天气）`  
  例：`场01. 圣城第九机甲维修区 · 露天工坊 · 夜（暴雨）`
- **出场角色卡（Characters Present）**：列出本场必须在场的所有角色。
- **动作段落（Action Blocks）**：以 `△` 开头，短句白描，动词先行。
- **对白与潜台词（Dialogue & Subtext）**：
  - 角色名居中加粗。
  - 括号内注明生理状态或微表情（微颤、咬牙、冷笑）。
  - 对白内容不可变、口播化、句式有力。

---

## 三、 剧本输出格式规范模板

### 1. 中文短剧标准剧本格式
```markdown
# 第 001 集：[集名]

> **单集时长**：90秒 | **核心爽点**：[身份反差/极致羞辱/金手指觉醒]  
> **片尾钩子**：[断点悬念]

---

### 场 01. 第九机甲维修区 · 露天泥泞工坊 · 夜（暴雨）
**出场人物**：林辰、赵工头、围观工人们  
**核心道具**：生锈扳手、黄铜传动轴  

△ （全景）暴雨倾盆。三十米高的残破蒸汽机甲如钢铁巨兽般耸立在雨幕中，排气管道喷吐刺鼻白烟。
△ （中景）林辰全身湿透，单膝跪在冰冷泥水里，双手握着重型扳手拧紧底盘螺栓。
△ （近景）赵工头嘴里嚼着烟草，带着两名打手大步走来，浑身湿漉漉的皮大衣滴落污泥。
△ （特写）赵工头猛地抬腿，厚重的铁头皮靴“砰”的一声狠狠踹在林辰背上！
△ 林辰失去平衡扑倒在泥水里，手中的扳手脱手砸在水坑中。
△ （特写）赵工头一脚重重踏在林辰右手手背上，将他的五指死死碾进碎石泥浆！

赵工头
（居高临下，啐了一口带血的唾沫）
“慢得像条死狗！今天修不好这台机器，你连泥汤都别想喝！”

△ 林辰脸颊紧贴泥泞，右臂青筋暴起，但眼神冰冷如铁。

林辰
（喉结滚动，从牙缝中挤出）
“传动轴修好了。我的工钱。”
```

---

### 2. 出海短剧标准剧本格式（英文角色名 + 中文动作 + 英文地道对白）
```markdown
# Episode 001: The Dragon's Spark

> **Format**: Overseas Vertical Micro-Drama (9:16) | **Target Platforms**: ReelShort / DramaBox / ShortMax  
> **Duration**: 90s | **Core Hook**: Extreme class oppression & mysterious dragonfire mark awakening

---

### Scene 01. Sector Nine Mecha Repair Bay · Open Yard · Night (Heavy Rain)
**Characters**: Lucas, Grover, Factory Workers  
**Key Props**: Heavy iron ratchet wrench, brass transmission shaft  

△ （全景）暴雨如注，黑夜浓稠如机油。数台残破的巨型蒸汽机甲在雨幕中耸立，蒸汽排气阀嘶嘶喷吐白雾。
△ （中景）Lucas 全身湿透，精壮的手臂裸露在磨损的短袖牛仔工服外，正单膝跪在泥浆里拧紧最后一枚轴承螺母。
△ （特写）靴底破空声炸响！工头 Grover 狞笑着抬起沉重的铁头军靴，暴力一脚踹中 Lucas 的后背！
△ Lucas 脊椎震颤，身体向前冲跌扑入泥水池中，手中的铁扳手脱手落在手掌旁。
△ （特写）Grover 跨步上前，沾满烂泥的钢头战靴“啪”的一声狠绝踏在 Lucas 的右手手背上，连同扳手柄一起死死碾入地底碎石！

Grover
（居高临下狞笑，向泥浆里啐出黑色烟草汁）
"Moving slow as a dead dog! Tune this rig tonight, or you won't even have mud water to drink!"
（中文潜台词：动作慢得像条死狗！今晚修不好这破机甲，你连泥水都没得喝！）

△ Lucas 侧脸紧贴湿泥，雨水冲刷着他额前的碎发，深邃的双眼透出野兽般的冷冽杀意。

Lucas
（咬紧牙关，声音沙哑低沉）
"Drive shaft is fixed. My wages."
（中文潜台词：传动轴修好了。我的工钱。）

△ Grover 闻言放声大笑，脚底鞋钉再次狠狠拧动，骨骼发出令人牙酸的挤压声。

Grover
（嘲讽大笑，眼神凶戾）
"Wages? A nameless gutter orphan dares to demand coin? Scrub the battle deck tonight, or burn in the furnace!"
（中文潜台词：工钱？一个没名没姓的阴沟孤儿也敢找我要钱？今晚滚去刷战舰甲板，否则把你塞进熔炉当柴烧！）
```

---

## 四、 平台适配矩阵指南

| 平台属性 | 平台名称 | 剧本核心技术指标与适配要求 |
| :--- | :--- | :--- |
| **国内短剧** | 抖音 / 快手 / 微信小程序 / 腾讯微短剧 | 单集 60~90 秒，9:16 竖屏居中构图，对白节奏紧迫，第一秒直接进戏，杜绝铺垫。 |
| **出海短剧** | ReelShort / DramaBox / ShortMax / TikTok | 单集 90~120 秒，**角色名严格使用英文**，动作中文，对白地道欧美短剧英语（Wolf/Billionaire/Revenge/Alpha 范式）。 |
| **影视/中剧** | 爱奇艺 / 优酷 / 腾讯横屏 / 独立短片 | 单集 5~10 分钟或单部 120 分钟，标准 Slugline，视听语言细腻，人物弧光深层铺垫。 |
| **动态漫/漫剧** | 快看漫画 / 哔哩哔哩漫剧 / 腾讯动漫 | 画面具象化拆分为九宫格画框，台词自带拟音字（轰！咔嚓！嘶！），对白便于做气泡框排版。 |
| **AI 视频管线** | MiniMax H3 / Kling / Runway Gen-3 / Sora | **动作解耦**：每个微镜头仅承载单动量，台词严格一字不差不可变，提供空间绝对站位与刚体锚点。 |

---

## 五、 生成前自检硬门禁（Pre-Output Checklist）

任何剧本在交付用户前，必须经由以下 6 项门禁审核：

1. **[角色命名门禁]** 若为出海模式，角色名是否 100% 为英文？绝无混用中文人名！
2. **[动作解耦门禁]** 是否存在单句塞入超过 2 个复合大动作的臃肿长句？必须拆解为原子微动量！
3. **[纯视觉化门禁]** 是否存在“心中想”、“回忆起当年”等不可拍摄的纯心理旁白？必须全量转译为外化动作！
4. **[三秒抓人门禁]** 第 001 集开篇前 3 秒是否已有明确危机、强视觉反差或强烈悬念？
5. **[断点钩子门禁]** 每集结尾是否卡在戏剧最高点或致命危机瞬间？严禁在对话完毕、危机解决后平淡收尾！
6. **[双语对照门禁]** 出海剧本的英文对白是否附带准确传神、便于监制把握语气的中文潜台词？
7. **[回钩门禁]**（长篇模式）第 2 集起，前 10 秒是否接住了上一集的钩子（兑现一半、再立新问题）？
8. **[预算门禁]**（长篇模式）对白 + V.O. 是否在单集预算内（120 秒 ≈ 150–220 英文词）？场次是否 ≤ 4？
9. **[账本门禁]**（长篇模式）信息差、道具状态、关系档位是否与 `03_连续性账本.md` 一致？
10. **[人设门禁]** 每个说话人的用词、句长、口头禅是否符合圣经里的语言档案？有没有人说了他“绝不会说”的话？主角本集有没有做一个**有代价的选择**？
11. **[资产门禁]** 出现的人物、造型、关键道具、场景都在 `bible.json` 里吗？（`bible_check.py --scripts` 无 ❌）

---

## 六、长篇改编模式（Long-Novel Mode）★

**何时启用：** 原著 ≥ 20 章，或目标 ≥ 30 集，或用户提到"压缩到 N 集""分集大纲""整本改编"。
**核心原则：** 集数由"可拍的强节拍"决定，不由章节数决定；**先规划、后写作**；**先找钩子点、再切集**。默认上限 60 集。

人物与资产：`references/character-and-dialogue.md`（欲望/需要/错误信念、压力下的选择、语言档案、潜台词、四种信息工具）与 `references/production-bible.md`（四层人物档案、ID 规则、造型/道具/场景/声线、导出资产库）。

详细方法：`references/long-novel-adaptation.md`（压缩工具箱、集数预算、分集卡片、单集 2 分钟结构）与 `references/episode-hook-system.md`（八种集尾钩子、强度阶梯、回钩写法、题材钩子库）。

| 步 | 做什么 | 命令 / 模板 | 门禁 |
| :--- | :--- | :--- | :--- |
| L0 立项参数 | 集数上限、时长、平台、尺度、V.O.、删哪些番外、红线 | `templates/adaptation/00_改编参数.md` | **用户确认** |
| L1 全书消化 | 扫描章节 → 按卷填节拍卡（summary / function / keep / emotion / hook_strength / info_changes） | `python3 scripts/chapter_index.py <正文目录>` | 每章节拍卡填完 |
| L2 压缩决策 | 支线、角色、场景、重复桥段、前移、内心外化 | `templates/adaptation/02_压缩决策.md` | 每项有结论 + 理由 |
| L2.5 制作圣经 | 人物四层档案（戏剧/语言/视觉/声音）、造型（按阶段，同人换装=新 ID）、道具生命周期、场景、声线 | `templates/adaptation/bible.example.json` → `python3 scripts/bible_check.py adaptation/bible.json`；要接 AI 视频管线加 `--export-h3 <目录>` | ❌ 清零；主角人设用户确认 |
| L3 集数预算 | 按卷的作用加权分配集数；查付费墙/中点/高潮位置 | 写 `adaptation/arcs.json` → `python3 scripts/episode_budget.py adaptation/arcs.json --chapters adaptation/chapters.json` | 总数 ≤ 上限 |
| L4 分集大纲 | 每集：来源章节、回钩、目标、转折、≤4 场、集尾钩子（类型·强度·画面）、信息差 | 写 `adaptation/episodes.json` → `python3 scripts/outline_check.py adaptation/episodes.json --chapters adaptation/chapters.json --budget adaptation/budget.json` | ❌ 清零 + **用户逐集审过** |
| L5 逐集写作 | 每批 5 集，按四步转译法写，套长篇模板 | `templates/adaptation/episode_template.md` → `python3 scripts/script_lint.py adaptation/scripts/`；`python3 scripts/bible_check.py adaptation/bible.json --scripts adaptation/scripts/` | ❌ 清零 |
| L6 账本与审计 | 每批更新账本；每卷写完通读一遍 | `templates/adaptation/03_连续性账本.md` | 账本与剧本一致 |

**执行纪律：**
1. L1 按卷分批读（有复盘卡/摘要先读卡，再抽查原文的对白和章尾）；节拍卡写回 `chapters.json`，不要只写在对话里。
2. L4 是整部剧质量的决定点：大纲没过用户审，不进 L5。
3. L5 写每一集前，先读：本集大纲卡、上一集最后一场、连续性账本。
4. 每集最后一行固定 `**【Episode NNN 完 · 集尾钩子：type】**`，钩子画面之后不再有台词。
5. 题材钩子要对路：言情/马甲类用"通知、穿帮、距离、宣示、临界"，不要照搬打脸剧的耳光和枪口（见钩子系统第五节）。

**长篇模式格式补充（兼容下游 AI 视频管线）：**
- 场次标题用三个井号：`### 场 NN. 地点 · 内/外 · 时间`。
- 说话人单独一行 `**Name**`；画外音 `**Name (V.O.)**`（后期配音，不进视频模型）。
- 手机/屏幕文字：`【屏幕 · 发送方 → 接收方】` 下接以 `>` 开头的行，每块 ≤ 4 行（生成时屏幕留空，后期叠字）。
- 开头信息区写：来源章节、开场回钩、本集目标、中段转折、集尾钩子、信息差。
