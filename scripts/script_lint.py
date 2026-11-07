#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L5 单集剧本编导一体质检器 v4.0（Cinematic Showrunner Edition）：
支持弹性电影片长（M01–M20 动态微切片）、首集世界观俯瞰与人物温度门禁、一段一空间检查、
AI 说明书独白 / 捧哏惊叹 / 伪潜台词雷达、动作解耦与集尾钩子硬门禁。

用法：
  python scripts/script_lint.py <剧本文件或目录>... [--mode overseas|cn] [--seg-words 28]
  （若剧本头部声明了 `**时长**：195 秒（13 段 × 15 秒）`，自动按该时长动态计算词数预算与场次上限！）
"""
import argparse
import re
import sys
from pathlib import Path

INTERIOR = ['心想', '心里', '内心', '心中', '暗想', '回忆起', '想起', '意识到', '感到', '觉得', '不由得', '心头', '暗暗决定']
CHAINS = ['随即', '然后', '顺势', '接着', '紧接着', '同时', '并且', '一边', '随后']
MASS_CROWD = ['数万', '上万', '成千上万', '数百名', '三千', '千军万马', '万人广场']

# AI 腔高危台词模式（说明书自言自语 / 反派廉价捧哏 / 新闻播报式前情复述）
AI_DIALOGUE_PATTERNS = [
    (re.compile(r"\bobeying me\b|\bwon't move\b|\bfade back\b|\beating my flesh\b", re.I),
     '疑似「AI 说明书式自言自语」→ 建议删掉解说独白，改用沉默、呼吸与直接物理行动'),
    (re.compile(r"\bwhat monster is (he|she|this)\b|\bsupposed to be ash\b|\bin one punch\?!", re.I),
     '疑似「反派捧哏工具人惊叹词」→ 建议改为实质威胁动作或简短失态指令'),
    (re.compile(r"\bmelted my hand,?\s+so\b|\blast night,?\s+so\b", re.I),
     '疑似「新闻播报式前情复述」→ 在场人已知的事实不要用嘴复盘'),
]

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

            for rx, hint in AI_DIALOGUE_PATTERNS:
                if rx.search(text):
                    warns.append(f'{speaker}: "{text[:42]}" → {hint}')

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
            chain = sum(act.count(w) for w in CHAINS)
            if chain >= 2:
                warns.append(f'一行里动作太多（{chain} 个连接词）→ 拆成多行，一行一个动作：{act[:30]}')
            elif len(CJK.findall(act)) > 72:
                warns.append(f'动作行过长（{len(CJK.findall(act))} 字）→ 拆行：{act[:30]}')
        elif s.startswith('#') or s.startswith('**出场') or s.startswith('**核心') or s.startswith('**造型'):
            speaker = None

    # 首集电影级开场定场检查（仅提示 EP001）
    if ep_no == 1 and m01_actions:
        joined_m01 = ' '.join(m01_actions)
        if not any(k in joined_m01 for k in ('大远景', '远景', '俯瞰', '俯视', '航拍', '全景', 'Crane Down')):
            warns.append('EP001 开场 M01 缺少世界观大远景/俯瞰定场镜头（易导致首集开头过硬、缺乏空间锚点）')

    # 一段一空间检查
    for seg, sc_set in sorted(seg_scenes.items()):
        if len(sc_set) > 1:
            warns.append(f'分段 {seg} 横跨了多个场次 {sorted(sc_set)} → 违反「一段一主空间」铁律，易造成 AI 视频空间瞬移穿帮')

    for seg, cnt in sorted(seg_words.items()):
        if cnt > a.seg_words:
            warns.append(f'分段 {seg} 对白 {cnt} 词，超过 15 秒微切片上限 {a.seg_words} 词（易导致 H3/Kling 吞字或口型加速）')

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
    ap.add_argument('--seg-words', type=int, default=28, help='单段 15 秒微切片对白上限（英文词默认 28，cn 模式建议 55）')
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
