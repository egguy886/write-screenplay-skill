# 出海微短剧创作与语言规范协议（Overseas Script Protocol）

## 一、 语言三层分立铁律（The 3-Tier Language Principle）

在出海剧本模式下，严格遵循三层语言分立，这是保证**国内主创团队把控视听调度**、**后续 AI 分镜工具精准编译**与**海外受众无违和感观看**的最佳实践：

```text
┌───────────────────────────────────────────────────────────────┐
│ 1. 角色命名（Character Names）  ➔ 100% 纯英文（Lucas, Grover） │
│ 2. 场景与动作（Slugline & Action）➔ 100% 纯中文（白描运镜与调度） │
│ 3. 角色对白（Dialogue）         ➔ 地道美语 + 括号中文潜台词   │
└───────────────────────────────────────────────────────────────┘
```

### 1. 角色名命名库（建议命名风格）
出海短剧主要面向欧美、拉美、东南亚英文受众，角色名需符合类型期待：
- **男主（Alpha/Billionaire/Avenger）**：`Lucas`, `Ethan`, `Adrian`, `Damian`, `Alexander`, `Tristan`, `Kaiser`
- **女主（Luna/Heiress/Cinderella）**：`Chloe`, `Scarlett`, `Elara`, `Aria`, `Serena`, `Vivian`, `Nora`
- **反派/恶毒配角（Beta/Rival/Cruel Boss）**：`Grover`, `Richard`, `Vance`, `Marcus`, `Elena`, `Victoria`, `Cassandra`

### 2. 动作与场景说明保持中文的深层原因
- **国内编导团队审阅**：国内短剧出海团队的制片人、导演、分镜师通常为中文母语者，全中文的场景描述能最高效传递镜头情绪。
- **AI 视频工作流兼容**：本项目下游的 `ai-storyboard-director`、`drama-h3-prompts`、`minimax-h3-video` 等工具均以中文为主要调度分析语言，便于将动作映射到刚体锚点和相机轨道。

### 3. 对白编写规范（地道美语 + 中文潜台词）
- **杜绝中式直译（Chinglish）**：
  - 错误示例：*"You eat leopard gall, dare to hit me!"* (你吃了豹子胆)
  - 正确示例：*"You've got a death wish, boy!"*
- **必须附带括号中文潜台词**：
  - 便于国内监制与配音指导确认演员口吻与情绪分寸。
  - 示例：
    ```text
    Lucas: "Drive shaft is fixed. My wages."
    （中文潜台词：传动轴修好了。把我的工钱结了。）
    ```

---

## 二、 出海主流四大题材与经典核心梗（Core Tropes）

### 1. 狼人与宿命伴侣（Werewolf & Alpha Romance）
- **核心关键词**：`Mate`（命中注定伴侣）、`Reject`（当众退婚/拒绝）、`Alpha King`（最高统治者）、`Rogue`（无族流浪狼）。
- **经典开局**：女主被家族或前任 Alpha 当众残酷拒绝并驱逐，沦为弱者，随后在禁忌森林或拍卖会中偶遇至高无上的 Alpha King，瞬间触发灵魂共鸣（Mate Bond）。

### 2. 隐藏身份的亿万富翁（Billionaire in Disguise）
- **核心关键词**：`Undercover`（隐姓埋名）、`Black Card`（黑金无限卡）、`Dumped`（遭拜金女甩掉）。
- **经典开局**：首富为了考验真爱或微服私访伪装成清洁工/外卖员，在高级餐厅被拜金前女友和跋扈富二代当众践踏，下半集劳斯莱斯车队与特助空降现场。

### 3. 契约婚姻与先婚后爱（Contract Marriage）
- **核心关键词**：`One-Night Stand`（荒唐一夜）、`Secret Marriage`（隐婚）、`Cold CEO`（禁欲冷血总裁）。
- **经典开局**：为拯救破产家族或重病母亲，女主被迫与城中最有权势但传闻残废/冷血的顶级财阀签订一年契约婚姻协议。

### 4. 黑帮复仇与强制爱（Mafia Romance & Dark Revenge）
- **核心关键词**：`Don`（黑手党教父）、`Debt`（血债）、`Captive`（囚徒）、`Obsession`（病态占有欲）。
- **经典开局**：女主为了替父还债，落入冷血残酷的黑手党掌舵人手中，在生死边缘与危险暴徒展开心理攻防战。
