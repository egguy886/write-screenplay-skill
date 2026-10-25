#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L4 分集大纲校验：检查 episodes.json 的集数上限、章节覆盖、开场回钩、集尾钩子
（类型轮换 / 强度阶梯 / 付费墙）、场次数量，并生成可读的 04_分集大纲.md。

格式见 templates/adaptation/episodes.example.json。
用法：python3 scripts/outline_check.py adaptation/episodes.json [--chapters adaptation/chapters.json] [--budget adaptation/budget.json]
退出码：有 ❌ 时为 1。
"""
import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adapt_common import parse_ranges, fmt_ranges  # noqa: E402

HOOKS = {'reveal': '揭示', 'threat': '危机迫近', 'choice': '抉择', 'reversal': '反转',
         'almost': '情感临界', 'line': '金句', 'question': '悬问', 'arrival': '闯入', 'ending': '结局'}
LEVELS = {'small': 1, 'mid': 2, 'big': 3}
LEVEL_CN = {'small': '小', 'mid': '中', 'big': '大'}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('episodes_json')
    ap.add_argument('--chapters', help='chapters.json：核对每章都被覆盖或明确删除')
    ap.add_argument('--budget', help='budget.json：核对每集所属卷与预算一致')
    ap.add_argument('--max-scenes', type=int, default=4)
    a = ap.parse_args()

    path = Path(a.episodes_json)
    cfg = json.loads(path.read_text(encoding='utf-8'))
    eps = sorted(cfg.get('episodes', []), key=lambda e: e.get('ep', 0))
    cap = int(cfg.get('max_episodes', 60))
    paywall = cfg.get('paywall_after')
    errs, warns = [], []
    E = lambda e: f"E{e.get('ep', '?'):02d}" if isinstance(e.get('ep'), int) else 'E??'

    # 集号
    nums = [e.get('ep') for e in eps]
    if len(eps) > cap:
        errs.append(f'共 {len(eps)} 集，超过上限 {cap}')
    if nums != list(range(1, len(eps) + 1)):
        errs.append(f'集号不连续或有重复：{nums[:10]}{"…" if len(nums) > 10 else ""}')

    # 章节覆盖
    cut = set()
    for c in cfg.get('cut', []):
        if not c.get('reason'):
            errs.append(f"cut {c.get('chapters')} 没写删除理由")
        cut.update(parse_ranges(c.get('chapters')))
    used, last_max = Counter(), 0
    for e in eps:
        src = parse_ranges(e.get('source'))
        if not src:
            errs.append(f'{E(e)} 没写来源章节 source')
            continue
        used.update(src)
        if min(src) < last_max - 3 and not e.get('chapters_note'):
            warns.append(f'{E(e)} 来源 Ch{fmt_ranges(src)} 比前面的集早 >3 章（倒叙/前移请在 chapters_note 说明）')
        last_max = max(last_max, max(src))
        bad = sorted(set(src) & cut)
        if bad:
            errs.append(f'{E(e)} 用到了已删除的章节 Ch{fmt_ranges(bad)}')
    if a.chapters:
        allch = {c['ch'] for c in json.loads(Path(a.chapters).read_text(encoding='utf-8'))['chapters']}
        lost = sorted(allch - set(used) - cut)
        if lost:
            errs.append(f'这些章节没被任何一集覆盖、也不在 cut：Ch{fmt_ranges(lost)}')
    spread = [c for c, n in used.items() if n > 2]
    if spread:
        warns.append(f'这些章节被 3 集以上引用（可能拆得太碎）：Ch{fmt_ranges(spread)}')

    # 逐集字段与钩子
    prev_types = []
    since_big = 0
    for i, e in enumerate(eps):
        tag = E(e)
        is_last = i == len(eps) - 1
        for k in ('title', 'goal', 'turn'):
            if not e.get(k):
                errs.append(f'{tag} 缺 {k}')
        if i > 0 and not e.get('open_payoff'):
            errs.append(f'{tag} 缺 open_payoff（前 10 秒怎么接住上一集的钩子）')
        sc = e.get('scenes') or []
        if not sc:
            errs.append(f'{tag} 没有场次')
        elif len(sc) > a.max_scenes:
            warns.append(f'{tag} 有 {len(sc)} 场，2 分钟的戏建议 ≤{a.max_scenes} 场')
        h = e.get('end_hook') or {}
        t, lv, tx = h.get('type'), h.get('level'), h.get('text', '')
        if t not in HOOKS:
            errs.append(f'{tag} end_hook.type={t!r} 不在 {list(HOOKS)}')
        if lv not in LEVELS:
            errs.append(f'{tag} end_hook.level={lv!r} 应为 small/mid/big')
        if len(tx.strip()) < 8:
            errs.append(f'{tag} end_hook.text 太短：要写成具体画面或台词')
        if t == 'ending' and not is_last:
            errs.append(f'{tag} 不是最后一集，不能用 ending 钩子')
        if t and len(prev_types) >= 2 and prev_types[-1] == prev_types[-2] == t:
            errs.append(f'{tag} 钩子类型 {t} 已连续 3 集，换一种')
        prev_types.append(t)
        since_big = 0 if lv == 'big' else since_big + 1
        if since_big >= 10:
            warns.append(f'{tag} 已连续 10 集没有 big 钩子')
            since_big = 0
        if paywall and e.get('ep') == paywall and lv != 'big':
            errs.append(f'{tag} 是付费墙（paywall_after={paywall}），集尾钩子必须是 big')
        nxt = eps[i + 1] if i + 1 < len(eps) else None
        if nxt and e.get('arc') and nxt.get('arc') and nxt['arc'] != e['arc'] and LEVELS.get(lv, 0) < 2:
            warns.append(f"{tag} 是「{e['arc']}」的最后一集，钩子建议 ≥ mid")
        if 'info_state' not in e:
            warns.append(f'{tag} 没写 info_state（信息差状态），戏剧反讽类故事必填')

    used_types = Counter(t for t in prev_types if t in HOOKS)
    if len(eps) >= 20:
        miss = [k for k in HOOKS if k != 'ending' and k not in used_types]
        if miss:
            warns.append(f"全剧没用过这些钩子类型：{', '.join(miss)}")
        if used_types:
            top, n = used_types.most_common(1)[0]
            if n / len(eps) > 0.35:
                warns.append(f'钩子类型 {top} 占 {n / len(eps):.0%}，太单一')

    if a.budget:
        b = json.loads(Path(a.budget).read_text(encoding='utf-8'))
        for arc in b['arcs']:
            got = [e for e in eps if e.get('arc') == arc['name']]
            if got and len(got) != arc['episodes']:
                warns.append(f"「{arc['name']}」预算 {arc['episodes']} 集，大纲写了 {len(got)} 集")

    # 输出 md
    md = [f"# 04 分集大纲（L4）· {cfg.get('title', '')}", '',
          f'- 共 {len(eps)} 集（上限 {cap}）；删除章节：{fmt_ranges(cut)}；付费墙：E{paywall}' if paywall else
          f'- 共 {len(eps)} 集（上限 {cap}）；删除章节：{fmt_ranges(cut)}',
          f"- 钩子分布：{'、'.join(f'{HOOKS[k]} {n}' for k, n in used_types.most_common())}", '']
    cur_arc = None
    for e in eps:
        if e.get('arc') != cur_arc:
            cur_arc = e.get('arc')
            md += [f'## {cur_arc}', '']
        h = e.get('end_hook') or {}
        md += [f"### {E(e)} {e.get('title', '')}　〔Ch{fmt_ranges(parse_ranges(e.get('source')))}〕"
               + ('　💰付费墙' if paywall and e.get('ep') == paywall else '')]
        if e.get('open_payoff'):
            md.append(f"- **回钩**：{e['open_payoff']}")
        md += [f"- **目标**：{e.get('goal', '')}", f"- **转折**：{e.get('turn', '')}"]
        for j, s in enumerate(e.get('scenes') or [], 1):
            md.append(f"- 场{j:02d} {s.get('place', '')}：{s.get('summary', '')}")
        md.append(f"- **集尾钩子**〔{HOOKS.get(h.get('type'), h.get('type'))}·{LEVEL_CN.get(h.get('level'), h.get('level'))}〕{h.get('text', '')}")
        if e.get('info_state'):
            md.append(f"- 信息差：{e['info_state']}")
        md.append('')
    md += ['## 校验结果', ''] + [f'- ❌ {x}' for x in errs] + [f'- ⚠ {x}' for x in warns] + (['- ✅ 全部通过'] if not errs and not warns else [])
    out = path.with_name('04_分集大纲.md')
    out.write_text('\n'.join(md) + '\n', encoding='utf-8')

    for x in errs:
        print('❌', x)
    for x in warns:
        print('⚠ ', x)
    print(f"{'❌' if errs else '✅'} {len(eps)} 集，❌ {len(errs)} / ⚠ {len(warns)} → {out}")
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
