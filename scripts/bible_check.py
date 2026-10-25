#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
制作圣经校验：人物 / 造型 / 道具 / 场景 / 声线（adaptation/bible.json，格式见 templates/adaptation/bible.example.json）。

  python3 scripts/bible_check.py adaptation/bible.json
      校验字段完整性、ID 唯一、别名冲突、引用关系、集号区间。
  python3 scripts/bible_check.py adaptation/bible.json --scripts adaptation/scripts/
      再与剧本交叉核对（说话人、**出场人物**、**造型**、**核心道具**、场次地点），
      并生成 05_分集资产表.md（每集用到的资产 + 每个资产出现几集 → 生图优先级）。
  python3 scripts/bible_check.py adaptation/bible.json --export-h3 <目录>
      导出 h3-drama-kit 资产库骨架：cast.json / props.json / scenes.json / acting.json / voices.json
      + asset_prompts.md（每个资产的参考图生成提示词）。
退出码：有 ❌ 时为 1。
"""
import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from adapt_common import parse_ranges, fmt_ranges  # noqa: E402

REQ = {
    'lead': ['role', 'want', 'need', 'misbelief', 'contradiction', 'first_entrance',
             'voice_sheet.rhythm', 'voice_sheet.catchphrases', 'voice_sheet.never_says',
             'visual.face', 'visual.hair', 'visual.signature', 'wardrobe', 'voice_casting.timbre'],
    'support': ['role', 'want', 'visual.signature', 'wardrobe', 'voice_casting.timbre'],
    'guest': ['role', 'wardrobe'],
}
SPEAKER = re.compile(r'^\*\*([^*【]+?)\*\*\s*$')
FIELD = re.compile(r'^\*\*(出场人物|造型|核心道具)\*\*\s*[:：]\s*(.+)$')
SCENE = re.compile(r'^###\s*场\s*(\d+)\s*[.．、:：]?\s*(.*)$')
PREFIX = ('Create a clean production reference image sheet for the live-action short drama "{title}". '
          'Use premium grounded live-action realism, natural skin and fabric texture with visible pores, physically '
          'plausible materials, and a neutral professional art-department presentation. This is a static reference sheet, '
          'not a video frame: no motion blur, no dialogue, no subtitles, no story action, no camera movement. '
          'Preserve the exact identity, age, proportions, wardrobe logic, spatial topology, material and state described '
          'below. Do not invent a logo, brand, readable text, readable number, signature, watermark or graphic interface. '
          'Leave documents, screens, labels and signs blank for post-production.')
NEG = ('Negative constraints: no readable text, no random letters or numbers, no logos, no watermark, no subtitles, '
       'no duplicated limbs, no extra fingers, no mirrored geography, no identity drift, no age drift, no costume change, '
       'no glamour fashion styling, no film grain or cinematic colour grade on character sheets, no unexplained prop, no extra people.')


def get(d, dotted):
    for k in dotted.split('.'):
        if not isinstance(d, dict):
            return None
        d = d.get(k)
    return d


def norm(s):
    return re.sub(r'\s+', ' ', str(s)).strip().lower()


def split_items(s):
    return [x.strip() for x in re.split(r'[,，、;；]', s) if x.strip()]


def check(bible, errs, warns):
    chars = bible.get('characters', [])
    wards = bible.get('wardrobe', [])
    props = bible.get('props', [])
    locs = bible.get('locations', [])
    ids, alias_owner = {}, {}

    def reg_id(i, kind):
        if not i:
            errs.append(f'{kind} 缺 id')
        elif i in ids:
            errs.append(f'ID 重复：{i}（{ids[i]} 与 {kind}）')
        else:
            ids[i] = kind

    def reg_alias(a, owner):
        k = norm(a)
        if not k:
            return
        if k in alias_owner and alias_owner[k] != owner:
            errs.append(f'名字/别名 "{a}" 同时属于 {alias_owner[k]} 和 {owner}')
        alias_owner[k] = owner

    for c in chars:
        reg_id(c.get('id'), f"人物 {c.get('name')}")
        tier = c.get('tier', 'support')
        if tier not in REQ:
            errs.append(f"{c.get('id')} tier={tier!r} 应为 lead/support/guest")
            continue
        for f in REQ[tier]:
            v = get(c, f)
            if v in (None, '', [], {}):
                (errs if tier == 'lead' else warns).append(f"{c.get('id')} {c.get('name')}（{tier}）缺 {f}")
        cp = get(c, 'voice_sheet.catchphrases') or []
        if len(cp) > 3:
            warns.append(f"{c.get('id')} 口头禅 {len(cp)} 条，建议 ≤3")
        sig = get(c, 'visual.signature') or []
        if tier == 'lead' and len(sig) > 2:
            warns.append(f"{c.get('id')} 标志性视觉符号 {len(sig)} 个，建议 1–2 个（太多观众记不住，AI 也锁不住）")
        for a in [c.get('name')] + c.get('aliases', []):
            reg_alias(a, c.get('id'))

    char_ids = {c['id'] for c in chars if c.get('id')}
    ward_ids = set()
    for w in wards:
        reg_id(w.get('id'), '造型')
        ward_ids.add(w.get('id'))
        if w.get('character') not in char_ids:
            errs.append(f"造型 {w.get('id')} 的 character={w.get('character')} 不存在")
        if not w.get('look_en'):
            errs.append(f"造型 {w.get('id')} 缺 look_en（参考图上看得见的样子）")
        if w.get('variant_of') and w['variant_of'] not in {x.get('id') for x in wards}:
            errs.append(f"造型 {w.get('id')} 的 variant_of={w['variant_of']} 不存在")
        if w.get('episodes'):
            try:
                parse_ranges(w['episodes'])
            except ValueError:
                errs.append(f"造型 {w.get('id')} episodes 格式不对：{w['episodes']}")
    for c in chars:
        for wid in c.get('wardrobe', []):
            if wid not in ward_ids:
                errs.append(f"{c.get('id')} 引用了不存在的造型 {wid}")
        n = len(c.get('wardrobe', []))
        if c.get('tier') == 'lead' and n > 12:
            warns.append(f"{c.get('id')} 有 {n} 套造型：每套都是一张参考图，建议主角 6–10 套")
    for p in props:
        reg_id(p.get('id'), f"道具 {p.get('name_cn')}")
        if not p.get('look_en'):
            errs.append(f"道具 {p.get('id')} 缺 look_en")
        if p.get('owner') and p['owner'] not in char_ids:
            errs.append(f"道具 {p.get('id')} owner={p['owner']} 不存在")
        for a in [p.get('name_cn')] + p.get('aliases', []):
            reg_alias(a, p.get('id'))
        if p.get('first_ep') and p.get('payoff_ep') and p['payoff_ep'] < p['first_ep']:
            errs.append(f"道具 {p.get('id')} 回收集早于首次出现")
        if p.get('owner') and not p.get('position') and any(k in str(p.get('look_en', '')).lower() for k in ('bracelet', 'ring', 'watch', 'cord')):
            warns.append(f"道具 {p.get('id')} 是佩戴物，写上 position（哪只手/哪个位置），AI 最容易左右颠倒")
    for l in locs:
        reg_id(l.get('id'), f"场景 {l.get('name_cn')}")
        if not l.get('look_en'):
            errs.append(f"场景 {l.get('id')} 缺 look_en")
        if not l.get('anchors_en'):
            warns.append(f"场景 {l.get('id')} 缺 anchors_en（空间锚点在画面左/右）")
        if not l.get('light_en'):
            warns.append(f"场景 {l.get('id')} 缺 light_en（单一主光源）")
        for a in [l.get('name_cn')] + l.get('aliases', []):
            reg_alias(a, l.get('id'))
    if len(locs) > 14:
        warns.append(f'场景资产 {len(locs)} 个，主场景建议 8–14 个')
    return alias_owner, ward_ids


def cross_check(bible, alias_owner, ward_ids, scripts, errs, warns):
    chars = {c['id']: c for c in bible.get('characters', [])}
    locs = bible.get('locations', [])
    usage = defaultdict(set)  # asset id -> episodes
    per_ep = {}
    unknown_props = defaultdict(set)
    files = []
    for p in scripts:
        files += sorted(p.glob('E*.md')) if p.is_dir() else [p]
    for f in files:
        m = re.search(r'E(\d+)', f.name)
        if not m:
            continue
        ep = int(m.group(1))
        got = defaultdict(set)
        for ln in f.read_text(encoding='utf-8').splitlines():
            s = ln.strip()
            sm = SPEAKER.match(s)
            if sm and '【' not in s:
                name = re.sub(r'\s*\((V\.O\.|O\.S\.|O\.C\.)\)\s*$', '', sm.group(1)).strip()
                cid = alias_owner.get(norm(name))
                if cid in chars:
                    got['char'].add(cid)
                else:
                    errs.append(f'{f.name}: 说话人 **{name}** 不在圣经里')
                continue
            fm = FIELD.match(s)
            if fm:
                kind, val = fm.groups()
                for item in split_items(val):
                    if kind == '出场人物':
                        cid = alias_owner.get(norm(item))
                        if cid in chars:
                            got['char'].add(cid)
                        elif not re.search(r'们|群|众|路人|服务生|保安|宾客|crowd|guests', item, re.I):
                            warns.append(f'{f.name}: 出场人物 "{item}" 不在圣经里（群演请写"宾客们"等）')
                    elif kind == '造型':
                        wid = item.split('=', 1)[-1].strip()
                        if wid in ward_ids:
                            got['ward'].add(wid)
                        else:
                            errs.append(f'{f.name}: 造型 "{item}" 不存在')
                    else:
                        pid = alias_owner.get(norm(item))
                        if pid and pid.startswith('P'):
                            got['prop'].add(pid)
                        else:
                            unknown_props[item].add(ep)
                continue
            sc = SCENE.match(s)
            if sc:
                head = sc.group(2)
                hit = [l['id'] for l in locs
                       if any(a and norm(a) in norm(head) for a in [l.get('name_cn')] + l.get('aliases', []))]
                if hit:
                    got['loc'].add(hit[0])
                else:
                    warns.append(f'{f.name}: 场次 "{head[:24]}" 匹配不到场景资产（在 locations.aliases 里补地点名）')
        per_ep[ep] = got
        for k in got:
            for a in got[k]:
                usage[a].add(ep)
    for item, eps in unknown_props.items():
        warns.append(f'未登记道具 "{item}"（E{fmt_ranges(eps)}）：关键道具补进 props，陈设可忽略')
    return per_ep, usage, files


def breakdown_md(bible, per_ep, usage, out):
    names = {}
    for c in bible.get('characters', []):
        names[c['id']] = c.get('name', '')
    for w in bible.get('wardrobe', []):
        names[w['id']] = w.get('name_cn', '')
    for p in bible.get('props', []):
        names[p['id']] = p.get('name_cn', '')
    for l in bible.get('locations', []):
        names[l['id']] = l.get('name_cn', '')
    md = [f"# 05 分集资产表 · {bible.get('title', '')}", '',
          '由 `bible_check.py --scripts` 生成。造型只统计剧本里写了 `**造型**` 行的场次。', '',
          '## 一、每集用到的资产', '', '| 集 | 人物 | 造型 | 道具 | 场景 |', '| :-- | :-- | :-- | :-- | :-- |']
    for ep in sorted(per_ep):
        g = per_ep[ep]
        md.append(f"| E{ep:02d} | {'、'.join(sorted(g['char']))} | {'、'.join(sorted(g['ward']))} | "
                  f"{'、'.join(sorted(g['prop']))} | {'、'.join(sorted(g['loc']))} |")
    md += ['', '## 二、资产出现频次（生图优先级：出现集数越多越先做、越要锁死）', '',
           '| 资产 | 名称 | 出现集数 | 首次 | 集号 |', '| :-- | :-- | --: | :-- | :-- |']
    for a, eps in sorted(usage.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        md.append(f"| {a} | {names.get(a, '')} | {len(eps)} | E{min(eps):02d} | {fmt_ranges(eps)} |")
    declared = {x['id'] for k in ('wardrobe', 'props', 'locations') for x in bible.get(k, [])}
    unused = sorted(declared - set(usage))
    md += ['', '## 三、圣经里登记了但剧本还没用到', '', ('、'.join(unused) if unused else '无')]
    out.write_text('\n'.join(md) + '\n', encoding='utf-8')


def export_h3(bible, outdir):
    outdir.mkdir(parents=True, exist_ok=True)
    title = bible.get('title', '')
    chars = {c['id']: c for c in bible.get('characters', [])}
    cast, acting, voices, prompts = {}, {}, [], [f'# 资产参考图提示词 · {title}', '']
    pre = PREFIX.format(title=title)
    for w in bible.get('wardrobe', []):
        c = chars.get(w['character'], {})
        v = c.get('visual', {})
        desc_en = v.get('en') or ', '.join(x for x in [str(v.get('age', '')), v.get('build', ''), v.get('face', ''), v.get('hair', ''), v.get('skin', '')] if x)
        noun, pos = {'female': ('woman', 'her'), 'male': ('man', 'his')}.get(c.get('gender'), ('person', 'their'))
        cast[w['id']] = {
            'name': c.get('name', ''), 'name_cn': f"{c.get('name', '')}（{w.get('name_cn', '')}）", 'kind': 'character',
            'base_en': f"the {c.get('age', '')}-year-old {noun} shown in {{P}}; {pos} face, hair and build match {{P}} exactly; {pos} skin is clean, smooth and evenly toned",
            'base_cn': f"{v.get('age', '')}，{v.get('face', '')}，{v.get('hair', '')}，{v.get('build', '')}；严格以 {{P}} 为准",
            'wear_en': w.get('look_en', ''), 'wear_cn': w.get('look_cn', ''),
            'voice_en': get(c, 'voice_casting.en') or get(c, 'voice_casting.timbre') or '',
            'aliases': c.get('aliases', []), 'episodes': w.get('episodes', ''),
            '_todo': '核对 base_en 与参考图一致；voice_id 有声线资产后再填',
        }
        prompts += [f"## {w['id']} {c.get('name', '')} · {w.get('name_cn', '')}", '```', pre, '',
                    'Layout (three panels side by side on a flat neutral mid-grey studio backdrop with soft even light): LEFT, a large three-quarter close-up portrait of the face and shoulders, eyes with small natural catchlights; MIDDLE, a full-body front view with the head cropped out of frame at the top edge; RIGHT, a full-body back view. Same real person and identical wardrobe in all three panels. Plain and unstyled: no cinematic lighting, no colour grade.',
                    '', f"Character: {c.get('name', '')}, {desc_en}. Signature: {'; '.join(v.get('signature', []))}. Wardrobe: {w.get('look_en', '')}. All characters are adults.",
                    '', NEG, '```', '']
    for cid, c in chars.items():
        a = c.get('acting')
        if a:
            acting[c.get('name', cid)] = {
                'ids': c.get('wardrobe', []), 'engine_cn': a.get('engine', ''), 'body_en': a.get('body', ''),
                'eyes_en': a.get('eyes', ''),
                'tics': {f't{i + 1}': {'en': t.get('en', ''), 'cn': t.get('cn', ''), 'trigger_cn': t.get('trigger', '')}
                         for i, t in enumerate(a.get('tics', []))}}
        vc = c.get('voice_casting') or {}
        if vc:
            voices.append({'character': c.get('name', ''), 'voice_id': f"VOICE-{c.get('name', cid).upper().replace(' ', '')}-v1",
                           'tier': vc.get('tier', 'prompt'), 'status': 'candidate', 'age_anchor': vc.get('age_anchor', ''),
                           'control_prompt': vc.get('en') or ', '.join(x for x in [vc.get('timbre'), vc.get('pitch'), vc.get('pace'), vc.get('accent')] if x),
                           'reference': vc.get('reference', '')})
    props = {}
    for p in bible.get('props', []):
        props[p['id']] = {'name_cn': p.get('name_cn', ''), 'en': f"the {p.get('name_cn', '')} shown in {{P}}: {p.get('look_en', '')}",
                          'cn': p.get('look_cn', ''), 'match': [a for a in p.get('aliases', []) if re.match(r'[A-Za-z]', a)],
                          'position': p.get('position', ''), 'states': p.get('states', [])}
        prompts += [f"## {p['id']} {p.get('name_cn', '')}", '```', pre, '',
                    'Layout: 2x2 product-photo sheet on a neutral warm-grey surface with soft directional light from one side and a small contact shadow: hero three-quarter view, side view, top view, and a close detail; identical object, scale and wear in all four panels.',
                    '', f"Prop: {p.get('look_en', '')}. Screens, labels and documents are blank.", '', NEG, '```', '']
    scenes = {}
    for l in bible.get('locations', []):
        scenes[l['id']] = {'name': l['id'], 'name_cn': l.get('name_cn', ''), 'en': f"the {l.get('name_cn', '')} shown in {{P}}: {l.get('look_en', '')}",
                           'layout_en': f"Layout, fixed in every shot: {l.get('anchors_en', '')}", 'cn': l.get('look_cn', ''),
                           'light_en': l.get('light_en', '')}
        prompts += [f"## {l['id']} {l.get('name_cn', '')}", '```', pre, '',
                    'Layout: one single image, a high-angle three-quarter wide view of the empty location, camera high in one corner looking diagonally down at about 45 degrees; one single light source with one consistent shadow direction; no people. Every door, lamp, screen and curtain is shown in its state BEFORE any story action.',
                    '', f"Location: {l.get('look_en', '')}. Anchor: {l.get('anchors_en', '')}. Light: {l.get('light_en', '')}.", '', NEG, '```', '']
    dump = lambda name, obj: (outdir / name).write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding='utf-8')
    dump('cast.json', {'_说明': '由 write-screenplay bible_check.py 导出的骨架：每个造型一个 ID、一张参考图。核对 _todo 后并入 h3-drama-kit 项目 library/。', **cast})
    dump('props.json', {'_说明': '道具骨架。完整/损坏/带血是不同资产；屏幕标签留空。', **props})
    dump('scenes.json', {'_说明': '场景骨架。白天/夜晚/雨天是不同资产；可变物体画动作之前。', **scenes})
    dump('acting.json', {'_说明': '表演档案骨架。', **acting})
    dump('voices.json', {'_说明': '声线候选：用户试听确认前一律 candidate。', 'voices': voices})
    (outdir / 'asset_prompts.md').write_text('\n'.join(prompts) + '\n', encoding='utf-8')
    return len(cast), len(props), len(scenes), len(voices)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('bible')
    ap.add_argument('--scripts', nargs='+', help='剧本文件或目录（E001_xxx.md）')
    ap.add_argument('--export-h3', help='导出 h3-drama-kit 资产库骨架到这个目录')
    a = ap.parse_args()
    path = Path(a.bible)
    bible = json.loads(path.read_text(encoding='utf-8'))
    errs, warns = [], []
    alias_owner, ward_ids = check(bible, errs, warns)
    c = bible.get('characters', [])
    print(f"圣经：人物 {len(c)}（主角 {sum(x.get('tier') == 'lead' for x in c)}）· 造型 {len(bible.get('wardrobe', []))} · "
          f"道具 {len(bible.get('props', []))} · 场景 {len(bible.get('locations', []))}")
    if a.scripts:
        per_ep, usage, files = cross_check(bible, alias_owner, ward_ids, [Path(p) for p in a.scripts], errs, warns)
        out = path.with_name('05_分集资产表.md')
        breakdown_md(bible, per_ep, usage, out)
        print(f'剧本 {len(files)} 集 → {out}')
    if a.export_h3:
        n = export_h3(bible, Path(a.export_h3))
        print(f'导出 h3 骨架：造型 {n[0]} · 道具 {n[1]} · 场景 {n[2]} · 声线 {n[3]} → {a.export_h3}（含 asset_prompts.md）')
    for x in errs:
        print('❌', x)
    for x in warns:
        print('⚠ ', x)
    print(f"{'❌' if errs else '✅'} ❌ {len(errs)} / ⚠ {len(warns)}")
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main()
