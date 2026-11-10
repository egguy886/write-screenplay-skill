#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L5 单集剧本质检器 v4.1：
通用门禁（A 层）：英文角色名、去 AI 腔（说明书独白 / 复述 / 捧哏，通用句式，中英文都查）、
整集潜台词直译比例、回钩与集尾格式、比喻与心理描写、叠字数量、v2 拍表；
题材门禁（B 层，--genre 选用）：目前只查 G1 首集开场（action 要定场，romance 别用大远景定场）。
分镜层规则（一段一空间、每 15 秒词数）交给 h3-drama-kit；剧本里若仍标了 Mxx，才顺带提示。

用法：
  python scripts/script_lint.py <剧本文件或目录>... [--mode overseas|cn] [--genre action|revenge|romance|suspense|family]
  （剧本头部声明 `**时长**：195 秒` 时，按该时长放宽词数预算与场次上限）
"""
import argparse
import re
import sys
from pathlib import Path

INTERIOR = ['心想', '心里', '内心', '心中', '暗想', '回忆起', '想起', '意识到', '感到', '觉得', '不由得', '心头', '暗暗决定']
SIMILE = re.compile(r'像[^，。、]{0,14}|仿佛|好像|似的')   # 比喻句拍不出来（v2 规范）
CHAINS = ['随即', '然后', '顺势', '接着', '紧接着', '同时', '并且', '一边', '随后']
MASS_CROWD = ['数万', '上万', '成千上万', '数百名', '三千', '千军万马', '万人广场']

# AI 腔高危台词（v4.1：通用句式，不再只认示例剧本原话）。每条：(正则, 提示)
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
# 潜台词是不是“直译”：只看整集比例（单句判断不准）。真潜台词通常带意图词。
INTENT = re.compile(r"其实|故意|试探|逼|借机|掩饰|假装|装作|心里|真正|不敢|不想让|偏要|暗示|提醒|警告|讨好|拖延|拿捏|算计|激他|激她|威胁|示好|撒娇|嘴硬|台阶|赌|怕|想让|想要|要他|要她|别想|潜意|言外|——")

SEG_TAG = re.compile(r'\b(M(?:0[1-9]|1[0-9]|20))\b')
HEADER_DUR = re.compile(r'\*\*时长\*\*[:：]\s*(\d+)\s*秒')
HEADER_SEGS = re.compile(r'(\d+)\s*段\s*[×xX*]\s*15\s*秒')
SPEAKER = re.compile(r'^\*\*([^*【]+?)\*\*\s*$')
EN_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9 .'\-]*(\s*\((V\.O\.|O\.S\.|O\.C\.)\))?$")
QUOTE_LINE = re.compile(r'^\s*[“"](.+)[”"]\s*$')
END_LINE = re.compile(r'^\*\*【Episode\s+\d+\s*完\s*·\s*集尾钩子[:：]\s*([a-z]+)】\*\*\s*$')
EN_WORD = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")
CJK = re.compile(r'[一-鿿]')


def parse_episode_budget(head_text, default_sec, default_words, default_max_scenes):
    """根据剧本头部声明的弹性时长动态计算单集总词数上限与场次上限。"""
    sec = default_sec
    m_sec = HEADER_DUR.search(head_text)
    m_seg = HEADER_SEGS.search(head_text)
    if m_sec:
        sec = int(m_sec.group(1))
    elif m_seg:
        sec = int(m_seg.group(1)) * 15
    if sec != default_sec and default_sec == 120:
        scale = sec / 120.0
        words = int(round(default_words * scale))
        max_scenes = max(default_max_scenes, (sec + 24) // 25)
        return sec, words, max_scenes
    return sec, default_words, default_max_scenes


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
        errs.append('第一行应是 `# Episode NNN: 标题`')
    head = '\n'.join(content[:12])
    ep_sec, ep_word_limit, ep_max_scenes = parse_episode_budget(head, a.seconds, a.words, a.max_scenes)

    if '集尾钩子' not in head:
        warns.append('开头信息区缺「集尾钩子」说明')
    ep_no_m = re.search(r'(\d+)', content[0]) if content else None
    ep_no = int(ep_no_m.group(1)) if ep_no_m else 0
    if ep_no > 1 and ('开场回钩' not in head and '开场建置' not in head):
        warns.append('开头信息区缺「开场回钩」（怎么接住上一集钩子）')

    scenes = [ln for ln in content if re.match(r'^#{2,6}\s*场\s*\d+', ln.strip())]
    for ln in scenes:
        if not re.match(r'^###\s*场\s*\d+', ln.strip()):
            errs.append(f'场次标题要用三个井号：{ln.strip()[:30]}')
    if not scenes:
        errs.append('没有场次标题 `### 场 01. …`')
    elif len(scenes) > ep_max_scenes:
        warns.append(f'{len(scenes)} 场，当前时长（{ep_sec}s）建议 ≤{ep_max_scenes} 场')

    dlg_words = vo_words = n_action = 0
    speaker = None
    last_dialogue_idx = -1
    screen_run, in_screen = 0, False
    cur_seg = None
    cur_scene_no = 0
    seg_words = {}
    n_sub = n_literal = 0
    seg_scenes = {}
    m01_actions = []

    for i, raw in enumerate(content):
        s = raw.strip()
        sc_m = re.match(r'^###\s*场\s*(\d+)', s)
        if sc_m:
            cur_scene_no = int(sc_m.group(1))
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
            if speaker.endswith('(V.O.)'):
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
            elif len(CJK.findall(act)) > 72:
                warns.append(f'动作行过长（{len(CJK.findall(act))} 字）→ 拆行：{act[:30]}')
        elif s.startswith('#') or s.startswith('**出场') or s.startswith('**核心') or s.startswith('**造型'):
            speaker = None

    # 题材门禁 G1（只在选了题材时查 EP001 开场）
    WIDE = ('大远景', '远景', '俯瞰', '俯视', '航拍', '俯降', 'Crane Down')
    if ep_no == 1 and m01_actions and a.genre:
        joined = ' '.join(m01_actions[:2])
        if a.genre == 'action' and not any(k in ' '.join(m01_actions) for k in WIDE + ('全景',)):
            warns.append('[G1 action] EP001 开头缺定场镜头（大远景 / 俯降），观众没有空间和尺度的锚点')
        if a.genre == 'romance' and any(k in joined for k in WIDE):
            warns.append('[G1 romance] EP001 开头用了大远景 / 航拍定场：言情开场直接进尴尬或心动事件更快（genre-gates.md G1）')

    # 潜台词直译比例（A4）
    if n_sub >= 8 and n_literal / n_sub > 0.7:
        warns.append(f'[A4] 中文潜台词 {n_literal}/{n_sub} 句像台词直译（没有试探、掩饰、怕、故意之类的意图）→ 至少把关键几句写成没说出口的话')

    # 分镜层（剧本里若仍标了 Mxx 才提示；规则本身在 h3-drama-kit 执行）
    for seg, sc_set in sorted(seg_scenes.items()):
        if len(sc_set) > 1:
            warns.append(f'[分镜层] {seg} 横跨场次 {sorted(sc_set)}：剧本可以不切段，交给分镜按一段一空间切')
    for seg, cnt in sorted(seg_words.items()):
        if cnt > a.seg_words:
            warns.append(f'[分镜层] {seg} 对白 {cnt} 词 > {a.seg_words}：剧本可以不切段，交给分镜拆')

    # 集尾
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

    # —— v2 规范（观众先看懂）：叠字总量；若剧本用了 v2 信息区（有「本集一句话」），要求拍表和“上集观众记得什么” ——
    text = '\n'.join(content)
    n_overlay = len(re.findall(r'后期叠字', text))
    if n_overlay > 4:
        warns.append(f'后期叠字 {n_overlay} 处（建议 ≤2 处、每处 ≤6 个英文词；看懂测试里叠字揭秘最容易看不懂）')
    if '本集一句话' in '\n'.join(content[:20]):
        if '上集观众记得什么' not in '\n'.join(content[:20]):
            warns.append('v2 信息区缺「上集观众记得什么」（只写观众真在画面里见过的）')
        n_tab = len(re.findall(r'^\|\s*拍\s*\|', text, re.M))
        if n_tab < len(scenes):
            warns.append(f'v2：每场要有一张拍表（观众要懂 / 画面证据 / 台词 / 反应 / 必保），现在 {n_tab} 张、{len(scenes)} 场')
        if '| ✔ |' not in text and '✔ |' not in text:
            warns.append('v2：拍表里没有任何「必保 ✔」的拍；分镜靠它才知道哪几镜不能删')

    total = dlg_words + vo_words
    if total > ep_word_limit:
        errs.append(f'对白 {dlg_words} + V.O. {vo_words} = {total} 词，超过本集时长（{ep_sec}s）预算上限 {ep_word_limit}')
    if total >= 60 and vo_words > dlg_words * 0.25:
        warns.append(f'V.O. {vo_words} 词，超过对白的 25%，能外化的尽量外化')
    est = total / 2.5 + n_action * 1.8
    if est > ep_sec * 1.22:
        warns.append(f'估算时长 {est:.0f} 秒（对白 {total / 2.5:.0f}s + 动作 {n_action}×1.8s），明显超过声明时长 {ep_sec} 秒')
    n_segs = len(seg_words)
    seg_info = f' · 切片 {n_segs}段({ep_sec}s)' if n_segs else f' · 目标 {ep_sec}s'
    stats = f'场 {len(scenes)}{seg_info} · 对白 {dlg_words} · V.O. {vo_words} · 动作行 {n_action} · 估 {est:.0f}s'
    return errs, warns, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--mode', choices=['overseas', 'cn'], default='overseas')
    ap.add_argument('--words', type=int, default=220, help='120s 基准对白+V.O.上限（若剧本头部声明更长秒数则按比例自动放宽）')
    ap.add_argument('--genre', choices=['action', 'revenge', 'romance', 'suspense', 'family'], help='题材（选用 genre-gates.md 对应的题材门禁）')
    ap.add_argument('--seg-words', type=int, default=28, help='（分镜层，仅剧本标了 Mxx 时用）单段 15 秒对白上限')
    ap.add_argument('--seconds', type=int, default=120, help='默认基准时长（会被剧本头部的 **时长**：XXX 秒 自动覆盖）')
    ap.add_argument('--max-scenes', type=int, default=4, help='120s 基准最大场数（长集自动按比例放宽）')
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
