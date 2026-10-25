#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L1 节拍卡合并：把 Agent 分卷写好的节拍卡（Python 元组列表）合并写回 chapters.json。
分卷写、分批合并，避免一次性写 100+ 章的 JSON 出错；chapter_index.py 重跑时已填字段会保留。

卡片文件（adaptation/cards/*.py）格式：
  CARDS = [
    (章号, "一句话", function, keep, 情绪1-5, 钩子强度1-5, ["节拍",...], ["信息差变化",...], ["道具",...]),
  ]
  function ∈ trigger/escalate/reveal/twist/romance/payoff/setup/breather/filler
  keep     ∈ core/merge/montage/cut

用法：python3 scripts/merge_cards.py adaptation/chapters.json adaptation/cards/
"""
import importlib.util
import json
import sys
from pathlib import Path

FUNCS = {'trigger', 'escalate', 'reveal', 'twist', 'romance', 'payoff', 'setup', 'breather', 'filler'}
KEEPS = {'core', 'merge', 'montage', 'cut'}


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    jpath, cards_dir = Path(sys.argv[1]), Path(sys.argv[2])
    data = json.loads(jpath.read_text(encoding='utf-8'))
    by = {c['ch']: c for c in data['chapters']}
    n, bad = 0, []
    for f in sorted(cards_dir.glob('*.py')):
        spec = importlib.util.spec_from_file_location(f.stem, f)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        for row in getattr(m, 'CARDS', []):
            ch, summary, fn, keep, emo, hook, beats, info, props = row
            if ch not in by:
                bad.append(f'{f.name}: Ch{ch} 不存在')
                continue
            if fn not in FUNCS or keep not in KEEPS:
                bad.append(f'{f.name}: Ch{ch} function/keep 非法 {fn}/{keep}')
            if not (1 <= emo <= 5 and 1 <= hook <= 5):
                bad.append(f'{f.name}: Ch{ch} 情绪/钩子强度应为 1–5')
            by[ch].update(summary=summary, function=fn, keep=keep, emotion=emo, hook_strength=hook,
                          beats=beats, info_changes=info, props=props)
            n += 1
    missing = [c for c in by if not by[c]['summary']]
    jpath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'已合并 {n} 张；未填：{missing or "无"}')
    if bad:
        print('\n'.join('❌ ' + b for b in bad))
        sys.exit(1)


if __name__ == '__main__':
    main()
