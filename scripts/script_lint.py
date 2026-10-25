#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L5 单集剧本检查（长篇模式）：格式、对白预算、时长估算、内心戏、动作堆叠、集尾钩子。

检查项：
  ❌ 场次标题必须 `### 场 NN.`（四个井号下游读不到）；出海模式说话人必须英文名
  ❌ 最后一行必须是 `**【Episode NNN 完 · 集尾钩子：type】**`，钩子画面之后不能再有台词
  ❌ 对白+V.O. 超过预算（默认 220 词 / 120 秒）
  ⚠  英文台词后缺（中文潜台词：…）；台词里混中文
  ⚠  △ 动作行写心理（心想/意识到/回忆…）；一行塞多个动作；单行过长
  ⚠  场次 > 4；V.O. 超过对白 25%；屏幕文字块 > 4 行；估算时长超标；开头没有回钩说明

用法：python3 scripts/script_lint.py <剧本文件或目录>... [--mode overseas|cn] [--words 220] [--seconds 120]
"""
import argparse
import re
import sys
from pathlib import Path

INTERIOR = ['心想', '心里', '内心', '心中', '暗想', '回忆起', '想起', '意识到', '感到', '觉得', '不由得', '心头', '暗暗决定']
CHAINS = ['随即', '然后', '顺势', '接着', '紧接着', '同时', '并且', '一边', '随后']
SPEAKER = re.compile(r'^\*\*([^*【]+?)\*\*\s*$')
EN_NAME = re.compile(r"^[A-Za-z][A-Za-z0-9 .'\-]*(\s*\((V\.O\.|O\.S\.|O\.C\.)\))?$")
QUOTE_LINE = re.compile(r'^\s*[“"](.+)[”"]\s*$')
END_LINE = re.compile(r'^\*\*【Episode\s+\d+\s*完\s*·\s*集尾钩子[:：]\s*([a-z]+)】\*\*\s*$')
EN_WORD = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")
CJK = re.compile(r'[一-鿿]')


def lint(path, a):
    errs, warns = [], []
    lines = path.read_text(encoding='utf-8').splitlines()
    # 去掉末尾的格式注释和分隔线
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
    if '集尾钩子' not in head:
        warns.append('开头信息区缺「集尾钩子」说明')
    ep_no = re.search(r'(\d+)', content[0]) if content else None
    if ep_no and int(ep_no.group(1)) > 1 and '开场回钩' not in head:
        warns.append('开头信息区缺「开场回钩」（怎么接住上一集钩子）')

    scenes = [ln for ln in content if re.match(r'^#{2,6}\s*场\s*\d+', ln.strip())]
    for ln in scenes:
        if not re.match(r'^###\s*场\s*\d+', ln.strip()):
            errs.append(f'场次标题要用三个井号：{ln.strip()[:30]}')
    if not scenes:
        errs.append('没有场次标题 `### 场 01. …`')
    elif len(scenes) > a.max_scenes:
        warns.append(f'{len(scenes)} 场，2 分钟建议 ≤{a.max_scenes} 场')

    dlg_words = vo_words = n_action = 0
    speaker = None
    last_dialogue_idx = -1
    screen_run, in_screen = 0, False
    for i, raw in enumerate(content):
        s = raw.strip()
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
            last_dialogue_idx = i
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
            act = re.sub(r'^△\s*(（[^）]*）)?', '', s)
            hit = [w for w in INTERIOR if w in act]
            if hit:
                warns.append(f'动作行写了心理（{"/".join(hit)}）→ 外化成动作/道具/屏幕：{act[:30]}')
            chain = sum(act.count(w) for w in CHAINS)
            if chain >= 2:
                warns.append(f'一行里动作太多（{chain} 个连接词）→ 拆成多行，一行一个动作：{act[:30]}')
            elif len(CJK.findall(act)) > 70:
                warns.append(f'动作行过长（{len(CJK.findall(act))} 字）→ 拆行：{act[:30]}')
        elif s.startswith('#') or s.startswith('**出场') or s.startswith('**核心'):
            speaker = None

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
    if total > a.words:
        errs.append(f'对白 {dlg_words} + V.O. {vo_words} = {total} 词，超过预算 {a.words}')
    if total >= 60 and vo_words > dlg_words * 0.25:
        warns.append(f'V.O. {vo_words} 词，超过对白的 25%，能外化的尽量外化')
    est = total / 2.5 + n_action * 1.8
    if est > a.seconds * 1.15:
        warns.append(f'估算时长 {est:.0f} 秒（对白 {total / 2.5:.0f}s + 动作 {n_action}×1.8s），超过 {a.seconds} 秒')
    stats = f'场 {len(scenes)} · 对白 {dlg_words} · V.O. {vo_words} · 动作行 {n_action} · 约 {est:.0f}s'
    return errs, warns, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--mode', choices=['overseas', 'cn'], default='overseas')
    ap.add_argument('--words', type=int, default=220, help='对白+V.O. 上限（英文词；cn 模式为汉字数，建议 400）')
    ap.add_argument('--seconds', type=int, default=120)
    ap.add_argument('--max-scenes', type=int, default=4)
    a = ap.parse_args()

    files = []
    for p in map(Path, a.paths):
        files += sorted(p.glob('E*.md')) if p.is_dir() else [p]
    if not files:
        sys.exit('没找到剧本文件（目录下应为 E001_xxx.md）')
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
