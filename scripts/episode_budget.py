#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L3 集数预算：按"章节数 × 卷的角色权重"把总集数分给每一卷（最大余数法取整），
检查付费墙、中点、至暗时刻、高潮是否落在规定区间，输出 budget.json 和 budget.md。

arcs.json 格式见 templates/adaptation/arcs.example.json：
  total_episodes  目标集数；max_episodes 上限（默认 60）；free_episodes 免费集数
  cut_chapters    不进正剧的章节（例 "132-137"）
  fixed           {"卷名": 集数} 手动钉死某卷集数，其余自动重分
  arcs[]          {"name", "chapters": "1-18", "role": opening|build|midpoint|sweet|crisis|climax|resolution, "weight"(可选覆盖)}

用法：python3 scripts/episode_budget.py adaptation/arcs.json [--chapters adaptation/chapters.json]
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adapt_common import parse_ranges, fmt_ranges  # noqa: E402

WEIGHTS = {'opening': 1.25, 'build': 1.0, 'midpoint': 1.25, 'sweet': 0.8,
           'crisis': 1.25, 'climax': 1.2, 'resolution': 1.0}
ROLE_CN = {'opening': '开局', 'build': '推进', 'midpoint': '中点', 'sweet': '甜宠/喘息',
           'crisis': '危机', 'climax': '高潮', 'resolution': '收尾'}
# 角色所在卷的"结尾集"应落在全剧的哪个比例区间
ZONES = {'midpoint': (0.42, 0.60, '中点大反转应在 45–55% 附近'),
         'crisis': (0.65, 0.88, '至暗时刻应在 70–83% 附近'),
         'climax': (0.80, 0.97, '高潮应在 83–95% 附近')}


def allocate(arcs, total, fixed):
    free_total = total - sum(fixed.values())
    pool = [a for a in arcs if a['name'] not in fixed]
    score = {a['name']: len(a['chs']) * a['w'] for a in pool}
    s = sum(score.values()) or 1
    raw = {k: v / s * free_total for k, v in score.items()}
    alloc = {k: max(1, int(v)) for k, v in raw.items()}
    rest = free_total - sum(alloc.values())
    for k in sorted(raw, key=lambda k: raw[k] - int(raw[k]), reverse=True):
        if rest <= 0:
            break
        alloc[k] += 1
        rest -= 1
    while rest < 0:  # 每卷至少 1 集导致超额时，从压缩比最低的卷扣
        k = min((k for k in alloc if alloc[k] > 1), key=lambda k: len(next(a for a in pool if a['name'] == k)['chs']) / alloc[k])
        alloc[k] -= 1
        rest += 1
    alloc.update(fixed)
    return alloc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('arcs_json')
    ap.add_argument('--chapters', help='chapters.json，用来核对章节覆盖')
    a = ap.parse_args()

    cfg_path = Path(a.arcs_json)
    cfg = json.loads(cfg_path.read_text(encoding='utf-8'))
    total = int(cfg.get('total_episodes', 60))
    cap = int(cfg.get('max_episodes', 60))
    free = int(cfg.get('free_episodes', 10))
    cut = set(parse_ranges(cfg.get('cut_chapters')))
    fixed = {k: int(v) for k, v in (cfg.get('fixed') or {}).items()}
    errs, warns = [], []

    arcs = []
    for x in cfg['arcs']:
        role = x.get('role', 'build')
        if role not in WEIGHTS:
            errs.append(f"卷「{x['name']}」role={role} 不认识（可选：{', '.join(WEIGHTS)}）")
        chs = [c for c in parse_ranges(x['chapters']) if c not in cut]
        arcs.append({'name': x['name'], 'role': role, 'chs': chs,
                     'w': float(x.get('weight', WEIGHTS.get(role, 1.0)))})
    if total > cap:
        errs.append(f'total_episodes={total} 超过上限 {cap}')
    unknown = set(fixed) - {x['name'] for x in arcs}
    if unknown:
        errs.append(f'fixed 里的卷名不存在：{sorted(unknown)}')

    covered = [c for x in arcs for c in x['chs']]
    dup = sorted({c for c in covered if covered.count(c) > 1})
    if dup:
        errs.append(f'章节被多个卷重复包含：{fmt_ranges(dup)}')
    if a.chapters:
        allch = {c['ch'] for c in json.loads(Path(a.chapters).read_text(encoding='utf-8'))['chapters']}
        lost = sorted(allch - set(covered) - cut)
        if lost:
            errs.append(f'这些章节既不在任何卷里、也不在 cut_chapters：{fmt_ranges(lost)}')

    if errs:
        print('\n'.join('❌ ' + e for e in errs))
        sys.exit(1)

    alloc = allocate(arcs, total, fixed)
    n_in = len(covered)
    ratio_all = n_in / total
    rows, ep = [], 1
    for x in arcs:
        n = alloc[x['name']]
        lo, hi = ep, ep + n - 1
        ep += n
        r = len(x['chs']) / n
        rows.append({'name': x['name'], 'role': x['role'], 'chapters': fmt_ranges(x['chs']),
                     'n_chapters': len(x['chs']), 'episodes': n, 'range': f'E{lo:02d}–E{hi:02d}',
                     'first': lo, 'last': hi, 'ratio': round(r, 2)})
        if r > 3.5:
            warns.append(f"「{x['name']}」压缩比 {r:.1f}：超压缩，先砍支线/整段蒙太奇")
        elif r < 1.0:
            warns.append(f"「{x['name']}」压缩比 {r:.1f}：一章拆多集，注意注水")
        z = ZONES.get(x['role'])
        if z and not (z[0] <= hi / total <= z[1]):
            warns.append(f"「{x['name']}」结束于 E{hi}（{hi / total:.0%}）：{z[2]}")
    op = next((r for r in rows if r['role'] == 'opening'), None)
    if op and abs(op['last'] - free) > 2:
        warns.append(f"开局卷结束于 E{op['last']}，付费墙在 E{free}：两者最好对齐（±2 集），让开局卷的大钩子当付费墙")
    if ratio_all > 3.5:
        warns.append(f'全书压缩比 {ratio_all:.1f}：建议增加 cut_chapters 或分两季')

    out = {'total_episodes': total, 'chapters_in': n_in, 'chapters_cut': fmt_ranges(cut),
           'ratio': round(ratio_all, 2), 'arcs': rows, 'warnings': warns}
    cfg_path.with_name('budget.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')

    md = ['# 集数预算（L3）', '',
          f'- 目标 {total} 集（上限 {cap}）；进入正剧 {n_in} 章，删除 {fmt_ranges(cut)}；全书压缩比 **{ratio_all:.2f} 章/集**',
          f'- 付费墙：前 {free} 集免费', '',
          '| 卷 | 作用 | 章节 | 章数 | 集数 | 集号 | 章/集 |', '| :-- | :-- | :-- | --: | --: | :-- | --: |']
    for r in rows:
        md.append(f"| {r['name']} | {ROLE_CN.get(r['role'], r['role'])} | {r['chapters']} | {r['n_chapters']} | "
                  f"{r['episodes']} | {r['range']} | {r['ratio']} |")
    md += ['', '## 提醒'] + ([f'- ⚠ {w}' for w in warns] or ['- 无'])
    md += ['', '想改某卷集数：在 arcs.json 的 `fixed` 里写 `{"卷名": 集数}`，再跑一遍。']
    cfg_path.with_name('budget.md').write_text('\n'.join(md) + '\n', encoding='utf-8')

    print('\n'.join(md[2:]))


if __name__ == '__main__':
    main()
