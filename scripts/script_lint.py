#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L5 单集剧本质检器 v5.0（前制编导 & 空间站位锁 & 静音可读版）：
通用门禁（A1–A10）：
  - 角色名规范、去 AI 腔（说明书独白 / 复述 / 捧哏，中英文通用）、潜台词直译比例、回钩与集尾强钩子格式；
  - [v5.0 新增 A9] 物理子空间独立分场检查（❌ 拦截“女囚室与隔壁木牢”式复合子空间场标）+ 每场 `**开场站位**` 锚点核验；
  - [v5.0 新增 A10] “静音可读”因果检查（无外部触发源突兀躺回/装昏提示、未交代物理出处凭空掏关键道具提示）；
  - [v5.0 校准] 确定性双轨时长测算（中文 3.8 字/秒、英文 2.5 词/秒 + 横屏 3.2s/动作节拍、竖屏 2.5s/动作节拍）。

用法：
  python scripts/script_lint.py <剧本文件或目录>... [--mode overseas|cn] [--aspect auto|9:16|16:9|2.39:1] [--genre action|revenge|romance|suspense|family] [--strict-staging]
"""
import argparse
import re
import sys
from pathlib import Path

INTERIOR = ['心想', '心里', '内心', '心中', '暗想', '回忆起', '想起', '意识到', '感到', '觉得', '不由得', '心头', '暗暗决定']
SIMILE = re.compile(r'像[^，。、]{0,14}|仿佛|好像|似的')
CHAINS = ['随即', '然后', '顺势', '接着', '紧接着', '同时', '并且', '一边', '随后']
MASS_CROWD = ['数万', '上万', '成千上万', '数百名', '三千', '千军万马', '万人广场']

# v5.0 A9: 复合子空间场标检测（防止把两个独立子空间合并在一场戏里导致下游复用同一张场景参考图）
SUBSPACE_NOUN = r'(?:女囚室|男囚室|囚室|木牢|石牢|地牢|走廊|甬道|长廊|过道|隔壁[^·\s]{1,6}|窄道|赌桌|前厅|正厅|后院|偏厅|卧房|内室|外间|书房|柴房|厨房|门外|门内|洞口|山径|楼梯间|电梯厅|车内|天台|走廊拐角)'
COMPOSITE_SLUG = re.compile(rf'{SUBSPACE_NOUN}[^·\n]{{0,6}}[与和及兼/+][^·\n]{{0,8}}{SUBSPACE_NOUN}')
SPATIAL_ANCHOR = re.compile(r'(?:画左|画右|居中|前景|远景|背景|内侧|外侧|门内|门外|栏内|栏外|栅栏内|栅栏外|桌旁|桌前|桌后|床沿|窗边|墙角|石壁|为界|相对|背对|面朝|left|right|inside|outside)', re.I)

# v5.0 A10: 静音可读（姿态突变触发源 & 道具物理出处）
POSTURE_SLEEP = re.compile(r'(?:躺回|歪回|倒回|装昏|装睡|假寐|合眼歪回)')
EXTERNAL_TRIGGER = re.compile(r'(?:火光|灯火|灯影|火把|油灯|脚步|门响|锁响|开门|说话声|喝骂|咳嗽|逼近|晃来|传来)')
PROP_DRAW = re.compile(r'(?:掏出|摸出|拔出|抽出|亮出|摸走|顺走)[^，。；\n]{0,12}(?:匕首|短刀|长剑|钥匙|铜钥|碎碗|瓷片|毒针|暗器|手枪|令牌|密信|骨笛|竹哨)')
PROP_SOURCE = re.compile(r'(?:怀里|怀中|腰间|袖中|袖里|靴筒|包袱|衣襟|口袋|兜里|抽屉|桌底|枕下|草堆下|尸身|身上|皮坎肩)')

AI_EN = [
    (re.compile(r"\bmy (?:body|hands?|legs?|arms?|heart|blood|power|eyes?)\b[^.?!]{0,25}\b(?:won't|can't|isn't|is|are|keeps?)\b[^.?!]{0,15}\b(?:move|stop|listen|obey|respond|burn\w*|glow\w*|shak\w*|changing)\b"
                r"|\bit'?s (?:obeying|answering|responding to|listening to|controlling) me\b|\bwhat(?:'s| is) happening to me\b|\bthis (?:power|fire|energy|feeling|strength)\b[^.?!]{0,20}\b(?:is|it's)\b"
                r"|\bI can feel (?:it|the power|my)\b", re.I),
     '疑似「说明书式自言自语」（对空气解说自己的状态）→ 改用沉默、眼神和直接的物理动作'),
    (re.compile(r"\b(?:as you (?:all )?know|as we (?:all )?know|you (?:already )?know (?:that|how) (?:I|we|he|she)|like I (?:said|told you)|remember (?:when|how) (?:you|we|I)|(?:last night|yesterday),? (?:you|he|she|we|they) [^.?!]{3,40},? (?:so|and then|which is why)\b)", re.I),
     '疑似「新闻播报式复述」（向在场的人复述大家都知道的事）→ 删掉，或改成只有观众不知道的那一半'),
    (re.compile(r"\bwhat (?:kind of )?(?:monster|demon|power|strength)\b[^.?!]{0,12}\b(?:is|was|does) (?:he|she|this|that)\b|\bhow is (?:this|that) (?:even )?possible\b|\b(?:impossible|that's impossible)[!?]"
                r"|\bwho (?:the hell )?is (?:he|she|this guy|this woman)\?!|\bin (?:one|a single) (?:punch|blow|hit|strike)\b", re.I),
     '疑似「捧哏惊叹」（替主角喊“怎么可能”）→ 改成后退、手抖、换弹匣等失态动作，或一句实际的命令'),
]
AI_CN = [
    (re.compile(r"我的(?:身体|手|腿|心脏|血|力量)[^。！？]{0,8}(?:不受控制|动不了|在燃烧|在发光|在颤抖)|这股力量|它在(?:听我的|回应我)|我感觉到了[^。！？]{0,6}力量|我这是怎么了"),
     '疑似「说明书式自言自语」→ 改用沉默、眼神和动作'),
    (re.compile(r"你也知道|大家都知道|我早就说过|还记得(?:吗|那天|昨晚)|昨晚你[^。！？]{2,20}所以"),
     '疑似「复述腔」→ 在场的人都知道的事不要用嘴复盘'),
    (re.compile(r"怎么可能[！?？!]|这不可能|他(?:到底)?是什么(?:怪物|人)[！?？!]|一拳就|竟然[^。！？]{0,10}[！!]{1}"),
     '疑似「捧哏惊叹」→ 改成失态动作或实际行动'),
]
INTENT = re.compile(r"其实|故意|试探|逼|借机|掩饰|假装|装作|心里|真正|不敢|不想让|偏要|暗示|提醒|警告|讨好|拖延|拿捏|算计|激他|激她|威胁|示好|撒娇|嘴硬|台阶|赌|怕|想让|想要|要他|要她|别想|潜意|言外|——")

SEG_TAG = re.compile(r'\b(M(?:0[1-9]|1[0-9]|20))\b')
HEADER_DUR = re.compile(r'\*\*(?:单集|本集)?时长\*\*[:：]\s*(\d+)\s*(秒|分钟|分|s|min)')
HEADER_ASPECT = re.compile(r'\*\*画幅\*\*[:：]\s*(16:9|2\.39:1|9:16)')
HEADER_SEGS = re.compile(r'(\d+)\s*段\s*[×xX*]\s*15\s*秒')
SPEAKER = re.compile(r'^\*\*([^*【]+?)\*\*\s*$')
META_PREFIXES = ('#', '**出场', '**核心', '**造型', '**开场站位', '**场景站位')
EN_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9 .'\-]*(\s*\((V\.O\.|O\.S\.|O\.C\.)\))?$")
QUOTE_LINE = re.compile(r'^\s*[“"](.+)[”"]\s*$')
END_LINE = re.compile(r'^\*\*【Episode\s+\d+\s*完\s*·\s*集尾钩子[:：]\s*([a-z]+)】\*\*\s*$')
EN_WORD = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")
CJK = re.compile(r'[一-鿿]')


def parse_episode_budget(head_text, default_sec, default_words, default_max_scenes, cli_aspect='auto', mode='overseas'):
    """根据剧本头部声明的弹性时长与画幅（9:16 / 16:9 / 2.39:1）动态计算对白预算与场次上限，不设死限。"""
    sec = default_sec
    m_sec = HEADER_DUR.search(head_text)
    m_seg = HEADER_SEGS.search(head_text)
    if m_sec:
        val, unit = int(m_sec.group(1)), m_sec.group(2)
        sec = val * 60 if unit in ('分钟', '分', 'min') else val
    elif m_seg:
        sec = int(m_seg.group(1)) * 15
    m_asp = HEADER_ASPECT.search(head_text)
    aspect = m_asp.group(1) if (cli_aspect == 'auto' and m_asp) else (cli_aspect if cli_aspect != 'auto' else '9:16')
    scale = max(0.5, sec / 120.0)
    base_words = default_words if mode == 'overseas' else max(default_words, 300)
    words = int(round(base_words * scale))
    # v5.0 鼓励物理子空间独立拆场，放宽场数软上限以免误罚精细分场
    max_scenes = max(default_max_scenes, (sec + 17) // 18)
    if aspect in ('16:9', '2.39:1'):
        max_scenes = max(max_scenes, (sec + 14) // 15)
    return sec, words, max_scenes, aspect


def lint(path, a):
    errs, warns = [], []
    lines = path.read_text(encoding='utf-8').splitlines()
    body = []
    in_comment = False
    for ln in lines:
        s = ln.strip()
        if s.startswith('<!--'):
            in_comment = True
        if not in_comment:
            body.append(ln)
        if s.endswith('-->'):
            in_comment = False
    content = [ln for ln in body if ln.strip() and ln.strip() != '---']

    if not content or not re.match(r'^#\s*(Episode|第)\s*\d+', content[0].strip()):
        errs.append('第一行应是 `# Episode NNN: 标题` 或 `# 第 NNN 集：标题`')
    head = '\n'.join(content[:12])
    ep_sec, ep_word_limit, ep_max_scenes, ep_aspect = parse_episode_budget(
        head, a.seconds, a.words, a.max_scenes, a.aspect, a.mode
    )
    is_widescreen = ep_aspect in ('16:9', '2.39:1')

    if '集尾钩子' not in head:
        warns.append('开头信息区缺「集尾钩子」说明')
    ep_no_m = re.search(r'(\d+)', content[0]) if content else None
    ep_no = int(ep_no_m.group(1)) if ep_no_m else 0
    if ep_no > 1 and ('开场回钩' not in head and '开场建置' not in head):
        warns.append('开头信息区缺「开场回钩」（怎么接住上一集钩子）')

    scenes = [ln for ln in content if re.match(r'^#{2,6}\s*场\s*\d+', ln.strip())]
    for ln in scenes:
        s_ln = ln.strip()
        if not re.match(r'^###\s*场\s*\d+', s_ln):
            errs.append(f'场次标题要用三个井号：{s_ln[:30]}')
        m_comp = COMPOSITE_SLUG.search(s_ln)
        if m_comp:
            errs.append(
                f'[A9 子空间混场] 场标「{s_ln}」合并了多个物理子空间（{m_comp.group(0)}）→ '
                f'必须按子空间拆成独立的 `### 场 NN.` 并写出跨场过渡动作，否则下游会共用同一张场景图导致人物原地刷出'
            )
    if not scenes:
        errs.append('没有场次标题 `### 场 01. …`')
    elif len(scenes) > ep_max_scenes:
        warns.append(f'{len(scenes)} 场，当前时长（{ep_sec}s · {ep_aspect}）建议 ≤{ep_max_scenes} 场（若系子空间精细拆场可调高头部声明时长）')

    dlg_words = vo_words = n_action = 0
    speaker = None
    last_dialogue_idx = -1
    screen_run, in_screen = 0, False
    cur_seg = None
    cur_scene_no = 0
    scene_has_staging = {}
    scene_Order = []
    seg_words = {}
    n_sub = n_literal = 0
    seg_scenes = {}
    m01_actions = []
    prev_act_text = ''
    act_char_limit = 88 if is_widescreen else 72

    for i, raw in enumerate(content):
        s = raw.strip()
        sc_m = re.match(r'^###\s*场\s*(\d+)', s)
        if sc_m:
            cur_scene_no = int(sc_m.group(1))
            scene_Order.append((cur_scene_no, s))
            scene_has_staging.setdefault(cur_scene_no, None)
            speaker = None
            prev_act_text = ''
            continue

        if s.startswith('**开场站位**') or s.startswith('**场景站位**'):
            speaker = None
            if cur_scene_no:
                st_val = re.sub(r'^\*\*(?:开场|场景)站位\*\*[:：]\s*', '', s).strip()
                scene_has_staging[cur_scene_no] = st_val
                if not SPATIAL_ANCHOR.search(st_val):
                    warns.append(f'[A9 站位锁] 场 {cur_scene_no:02d} 的 `**开场站位**` 缺少空间锚点词（画左/画右/栅栏内外/桌旁/面朝等）：{st_val[:36]}')
            continue

        if any(s.startswith(px) for px in META_PREFIXES):
            speaker = None
            continue

        sm = SEG_TAG.search(s)
        if sm:
            cur_seg = sm.group(1)
            seg_words.setdefault(cur_seg, 0)
            if cur_scene_no:
                seg_scenes.setdefault(cur_seg, set()).add(cur_scene_no)

        m = SPEAKER.match(s)
        if m and not END_LINE.match(s):
            speaker = m.group(1).strip()
            if a.mode == 'overseas' and not EN_NAME.match(speaker):
                errs.append(f'说话人应为英文名：**{speaker}**')
            continue

        q = QUOTE_LINE.match(s)
        if q and speaker:
            text = q.group(1)
            n = len(CJK.findall(text)) if a.mode == 'cn' else len(EN_WORD.findall(text))
            if speaker.endswith('(V.O.)') or speaker.endswith('（V.O.）'):
                vo_words += n
            else:
                dlg_words += n
            if cur_seg:
                seg_words[cur_seg] = seg_words.get(cur_seg, 0) + n
            last_dialogue_idx = i

            for rx, hint in (AI_CN if a.mode == 'cn' else AI_EN):
                if rx.search(text):
                    warns.append(f'{speaker}: "{text[:42]}" → {hint}')
            sub_line = next((c.strip() for c in content[i + 1:i + 3] if '中文潜台词' in c), '')
            if sub_line:
                sub = re.sub(r'^（?中文潜台词[:：]\s*|）$', '', sub_line)
                n_sub += 1
                if not INTENT.search(sub) and len(CJK.findall(sub)) <= 2.4 * max(n, 1) + 6:
                    n_literal += 1

            if a.mode == 'overseas':
                if CJK.search(text):
                    warns.append(f'{speaker} 的英文台词里有中文：{text[:30]}')
                nxt = ' '.join(c.strip() for c in content[i + 1:i + 3])
                if '中文潜台词' not in nxt:
                    warns.append(f'{speaker}: "{text[:30]}…" 后缺（中文潜台词：…）')
            continue

        if s.startswith('【屏幕'):
            in_screen, screen_run, speaker = True, 0, None
            continue
        if s.startswith('>') and in_screen:
            screen_run += 1
            if screen_run == 5:
                warns.append(f'屏幕文字块超过 4 行（第 {i + 1} 行附近），拆成两块或删减')
            continue
        in_screen, screen_run = False, 0

        if s.startswith('△'):
            n_action += 1
            speaker = None
            if cur_seg == 'M01' or (cur_seg is None and n_action <= 3):
                m01_actions.append(s)
            act = re.sub(r'^△\s*(（[^）]*）)?', '', s)
            hit = [w for w in INTERIOR if w in act]
            if hit:
                warns.append(f'动作行写了心理（{"/".join(hit)}）→ 外化成动作/道具/屏幕：{act[:30]}')
            crowd_hit = [w for w in MASS_CROWD if w in act]
            if crowd_hit:
                warns.append(f'动作行含 AI 视频高危宏大群演词（{"/".join(crowd_hit)}）→ 建议降维为 2-3 人前景特写+局部背景：{act[:30]}')
            sm = SIMILE.search(act)
            if sm and not act.startswith('（想象'):
                warns.append(f'动作行有比喻「{sm.group(0)[:14]}」→ 镜头拍不出来，换成能拍的动作或删掉（v2 规范）：{act[:30]}')
            chain = sum(act.count(w) for w in CHAINS)
            if chain >= 2:
                warns.append(f'一行里动作太多（{chain} 个连接词）→ 拆成多行，一行一个动作：{act[:30]}')
            elif len(CJK.findall(act)) > act_char_limit:
                warns.append(f'动作行过长（{len(CJK.findall(act))} 字）→ 拆行：{act[:30]}')

            # v5.0 A10: 静音可读 — 躺回/装昏前需有可见触发源
            if POSTURE_SLEEP.search(act) and not EXTERNAL_TRIGGER.search(act) and not EXTERNAL_TRIGGER.search(prev_act_text):
                warns.append(
                    f'[A10 静音可读] 场 {cur_scene_no:02d} 动作行写「{POSTURE_SLEEP.search(act).group(0)}」，但本行与上一行 △ 均未见外部触发源（火光/脚步/开门声）→ 静音观看易误判为无故昏倒：{act[:32]}'
                )
            # v5.0 A10: 道具来源守恒 — 掏出武器/钥匙需指明物理位置
            if PROP_DRAW.search(act) and not PROP_SOURCE.search(act) and not PROP_SOURCE.search(prev_act_text):
                warns.append(
                    f'[A10 道具守恒] 场 {cur_scene_no:02d} 动作行写「{PROP_DRAW.search(act).group(0)}」，未指明从何处取出（如腰间/怀里/袖中/桌底）→ 下游易拍成凭空变出道具：{act[:32]}'
                )
            prev_act_text = act

    # v5.0 A9: 检查每场是否声明了 **开场站位**
    missing_staging = [sc_no for sc_no, _ in scene_Order if not scene_has_staging.get(sc_no)]
    if missing_staging:
        msg = f'[A9 站位锁] 场 {", ".join(f"{x:02d}" for x in missing_staging)} 缺少 `**开场站位**：…`（写明隔断/锚点物、人物内外与画左/画右朝向，防下游空间错位）'
        if a.strict_staging:
            errs.append(msg)
        else:
            warns.append(msg)

    WIDE = ('大远景', '远景', '俯瞰', '俯视', '航拍', '俯降', 'Crane Down')
    if ep_no == 1 and m01_actions and a.genre:
        joined = ' '.join(m01_actions[:2])
        if a.genre == 'action' and not any(k in ' '.join(m01_actions) for k in WIDE + ('全景',)):
            warns.append('[G1 action] EP001 开头缺定场镜头（大远景 / 俯降），观众没有空间和尺度的锚点')
        if a.genre == 'romance' and not is_widescreen and any(k in joined for k in WIDE):
            warns.append('[G1 romance·9:16] 竖屏言情 EP001 开头用了大远景定场：竖屏言情直接进尴尬或心动事件更快（横屏电影模式除外）')

    if n_sub >= 8 and n_literal / n_sub > 0.7:
        warns.append(f'[A4] 中文潜台词 {n_literal}/{n_sub} 句像台词直译 → 至少把关键几句写成没说出口的话')

    for seg, sc_set in sorted(seg_scenes.items()):
        if len(sc_set) > 1:
            warns.append(f'[分镜层] {seg} 横跨场次 {sorted(sc_set)}：剧本可以不切段，交给分镜按一段一空间切')
    for seg, cnt in sorted(seg_words.items()):
        if cnt > a.seg_words:
            warns.append(f'[分镜层] {seg} 对白 {cnt} 词 > {a.seg_words}：剧本可以不切段，交给分镜拆')

    end_idx = next((i for i in range(len(content) - 1, -1, -1) if END_LINE.match(content[i].strip())), None)
    if end_idx is None:
        errs.append('最后缺 `**【Episode NNN 完 · 集尾钩子：type】**`')
    else:
        if end_idx != len(content) - 1:
            errs.append('结束标记之后还有内容')
        if last_dialogue_idx > end_idx:
            errs.append('结束标记之后还有台词')
        tail = content[max(0, end_idx - 3):end_idx]
        if not any(t.strip().startswith('△') for t in tail) and last_dialogue_idx < end_idx - 4:
            warns.append('集尾最后几行没有画面（△），钩子要落在可拍的画面或台词上')

    text = '\n'.join(content)
    n_overlay = len(re.findall(r'后期叠字', text))
    if n_overlay > 4:
        warns.append(f'后期叠字 {n_overlay} 处（建议 ≤2 处）')
    if '本集一句话' in '\n'.join(content[:20]):
        if '上集观众记得什么' not in '\n'.join(content[:20]):
            warns.append('v2 信息区缺「上集观众记得什么」')
        n_tab = len(re.findall(r'^\|\s*拍\s*\|', text, re.M))
        if n_tab < len(scenes):
            warns.append(f'v2：每场要有一张拍表，现在 {n_tab} 张、{len(scenes)} 场')
        if '| ✔ |' not in text and '✔ |' not in text:
            warns.append('v2：拍表里没有任何「必保 ✔」的拍')

    total = dlg_words + vo_words
    if total > ep_word_limit:
        errs.append(f'对白 {dlg_words} + V.O. {vo_words} = {total} 词/字，超过本集时长（{ep_sec}s）预算上限 {ep_word_limit}')
    if total >= 60 and vo_words > dlg_words * 0.25:
        warns.append(f'V.O. {vo_words} 词/字，超过对白的 25%，能外化的尽量外化')

    speech_rate = 3.8 if a.mode == 'cn' else 2.5
    shot_sec = 3.2 if is_widescreen else 2.5
    est = total / speech_rate + n_action * shot_sec
    if est > ep_sec * 1.25:
        warns.append(
            f'确定性估算时长 {est:.0f} 秒（对白 {total / speech_rate:.0f}s + 动作节拍 {n_action}×{shot_sec}s），高于头部声明时长 {ep_sec} 秒 → 建议调高头部 `**时长**` 给足动作呼吸，切勿下游强压碎切'
        )
    n_segs = len(seg_words)
    seg_info = f' · 切片 {n_segs}段({ep_sec}s)' if n_segs else f' · {ep_aspect} 声明 {ep_sec}s'
    stats = f'场 {len(scenes)}{seg_info} · 对白 {dlg_words} · V.O. {vo_words} · 动作行 {n_action} · 真实估时 {est:.0f}s'
    return errs, warns, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--mode', choices=['overseas', 'cn'], default='overseas')
    ap.add_argument('--aspect', choices=['auto', '9:16', '16:9', '2.39:1'], default='auto', help='画幅规格（auto 自动读取剧本头部的 **画幅**）')
    ap.add_argument('--words', type=int, default=220, help='120s 基准对白+V.O.上限（中文模式默认至少 300 字，按声明时长线性伸缩）')
    ap.add_argument('--genre', choices=['action', 'revenge', 'romance', 'suspense', 'family'], help='题材（选用 genre-gates.md 对应的题材门禁）')
    ap.add_argument('--seg-words', type=int, default=28, help='（分镜层，仅剧本标了 Mxx 时用）单段 15 秒对白上限')
    ap.add_argument('--seconds', type=int, default=120, help='默认基准时长（会被剧本头部的 **时长**：XXX 秒/分钟 自动覆盖）')
    ap.add_argument('--max-scenes', type=int, default=5, help='120s 基准最大场数（长集与横屏电影模式自动按比例放宽）')
    ap.add_argument('--strict-staging', action='store_true', help='将缺少 **开场站位** 从 ⚠ 提升为 ❌ 硬门禁')
    a = ap.parse_args()

    files = []
    for p in map(Path, a.paths):
        if p.is_dir():
            cand = sorted(p.glob('ep*.md')) or sorted(p.glob('E*.md'))
            files += [x for x in cand if '.before-polish' not in x.name and '.polish-report' not in x.name]
        else:
            files.append(p)
    if not files:
        sys.exit('没找到剧本文件')
    bad = 0
    for f in files:
        errs, warns, stats = lint(f, a)
        bad += bool(errs)
        print(f"{'❌' if errs else ('⚠ ' if warns else '✅')} {f.name}　{stats}")
        for x in errs:
            print('   ❌', x)
        for x in warns:
            print('   ⚠ ', x)
    print(f'\n{len(files)} 集，{bad} 集有 ❌')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
