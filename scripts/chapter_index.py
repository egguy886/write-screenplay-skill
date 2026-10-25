#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
L1 章节索引：扫描小说正文目录，给每章算字数、对白量、对白占比，抽出章尾段落，
配对复盘卡/摘要文件，生成 adaptation/chapters.json（节拍卡骨架）和 01_章节索引.md。

再次运行时保留 Agent 已填写的字段（summary / beats / function / keep / emotion /
hook_strength / info_changes / props / notes），只刷新客观数据。

用法：
  python3 scripts/chapter_index.py <正文目录> [--out <小说目录>/adaptation]
         [--chapter-re REGEX] [--card-re REGEX]
"""
import argparse
import json
import re
import sys
from pathlib import Path

CHAPTER_RE = r'(?i)^(?:ch(?:apter)?[_ \-]?0*(\d+)|第0*(\d+)章)'
CARD_RE = r'(?i)(?:walkthrough|复盘|card|summary|摘要)[_ \-]?0*(\d+)'
FILL_FIELDS = {
    "summary": "", "beats": [], "function": "", "keep": "", "emotion": None,
    "hook_strength": None, "info_changes": [], "props": [], "notes": "",
}
EN_WORD = re.compile(r"[A-Za-z]+(?:['’][A-Za-z]+)?")
CJK = re.compile(r'[一-鿿]')
QUOTE = re.compile(r'[“"]([^”"\n]+)[”"]|「([^」\n]+)」')
# 聊天/短信行：**Name:** message 或 Name：message
CHAT = re.compile(r'^\s*(?:\*\*[^*\n]{1,40}[:：]\*\*|[A-Za-z][A-Za-z .]{0,30}[:：]|[\u4e00-\u9fff]{1,6}[:：])\s*(.+)$', re.M)


def first_num(m):
    return int(next(g for g in m.groups() if g))


def measure(text):
    body = re.sub(r'^#.*$', '', text, flags=re.M)
    en, cjk = len(EN_WORD.findall(body)), len(CJK.findall(body))
    lang = 'cn' if cjk > en else 'en'
    count = (lambda t: len(CJK.findall(t))) if lang == 'cn' else (lambda t: len(EN_WORD.findall(t)))
    chat_lines = CHAT.findall(body)
    no_chat = CHAT.sub('', body)
    dwords = count(' '.join(a or b for a, b in QUOTE.findall(no_chat)))
    twords = count(' '.join(chat_lines))
    words = cjk if lang == 'cn' else en
    return lang, words, dwords, twords


def tail_of(text, limit=320):
    paras = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip() and not p.strip().startswith('#')]
    out = ''
    for p in reversed(paras):
        if p in ('---', '***', '* * *'):
            continue
        out = p + ('\n' + out if out else '')
        if len(out) >= limit // 2:
            break
    return out[-limit:]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('novel_dir')
    ap.add_argument('--out', help='输出目录，默认 <正文目录的上级>/adaptation')
    ap.add_argument('--chapter-re', default=CHAPTER_RE)
    ap.add_argument('--card-re', default=CARD_RE)
    a = ap.parse_args()

    src = Path(a.novel_dir).expanduser().resolve()
    out = Path(a.out).expanduser() if a.out else src.parent / 'adaptation'
    out.mkdir(parents=True, exist_ok=True)
    chap_re, card_re = re.compile(a.chapter_re), re.compile(a.card_re)

    chapters, cards = {}, {}
    for f in sorted(src.iterdir()):
        if f.suffix.lower() not in ('.md', '.txt'):
            continue
        mc = card_re.search(f.name)
        if mc:
            cards[first_num(mc)] = f
            continue
        m = chap_re.search(f.name)
        if m:
            chapters[first_num(m)] = f
    if not chapters:
        sys.exit(f'❌ {src} 里没找到章节文件（文件名需匹配 {a.chapter_re}）')

    jpath = out / 'chapters.json'
    old = {}
    if jpath.exists():
        old = {c['ch']: c for c in json.loads(jpath.read_text(encoding='utf-8')).get('chapters', [])}

    rows, lang_seen = [], set()
    for n in sorted(chapters):
        f = chapters[n]
        text = f.read_text(encoding='utf-8', errors='ignore')
        lang, words, dwords, twords = measure(text)
        lang_seen.add(lang)
        h = re.search(r'^#\s*(.+)$', text, flags=re.M)
        row = {
            "ch": n, "file": str(f), "title": h.group(1).strip() if h else f.stem,
            "words": words, "dialogue_words": dwords,
            "dialogue_ratio": round(dwords / words, 3) if words else 0.0,
            "texting_words": twords,
            "spoken_ratio": round((dwords + twords) / words, 3) if words else 0.0,
            "tail": tail_of(text), "card": str(cards[n]) if n in cards else "",
        }
        prev = old.get(n, {})
        for k, v in FILL_FIELDS.items():
            row[k] = prev.get(k, v)
        rows.append(row)

    nums = sorted(chapters)
    missing = [i for i in range(nums[0], nums[-1] + 1) if i not in chapters]
    unit = '字' if lang_seen == {'cn'} else '词'
    total = sum(r['words'] for r in rows)
    jpath.write_text(json.dumps({"source": str(src), "unit": unit, "total_words": total,
                                 "chapters": rows}, ensure_ascii=False, indent=2), encoding='utf-8')

    filled = sum(1 for r in rows if r['summary'] and r['keep'] and r['hook_strength'])
    lines = [
        '# 01 章节索引（L1）', '',
        f'- 来源：`{src}`',
        f'- 章节：{len(rows)}（Ch{nums[0]}–Ch{nums[-1]}）；复盘卡/摘要：{len(cards)}；缺号：{missing or "无"}',
        f'- 总量：{total:,} {unit}；平均每章 {total // len(rows):,} {unit}',
        f'- 节拍卡已填：{filled}/{len(rows)}',
        '', '| 章 | 标题 | 字数 | 对白占比 | 短信词数 | function | keep | 情绪 | 钩子 | 一句话 |',
        '| :-- | :-- | --: | --: | --: | :-- | :-- | :-: | :-: | :-- |',
    ]
    for r in rows:
        low = ' ⚠' if r['spoken_ratio'] < 0.15 else ''
        lines.append(f"| {r['ch']} | {r['title'][:40]} | {r['words']:,} | {r['dialogue_ratio']:.0%}{low} | {r['texting_words']} | "
                     f"{r['function']} | {r['keep']} | {r['emotion'] or ''} | {r['hook_strength'] or ''} | {r['summary']} |")
    lines += ['', '⚠ = 对白 + 短信 < 全章 15%：内心/叙述为主，优先考虑浓缩或外化。短信多的章适合用手机屏幕外化。']
    (out / '01_章节索引.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

    print(f'✅ {len(rows)} 章，{total:,} {unit}；复盘卡 {len(cards)}；缺号 {missing or "无"}')
    print(f'   节拍卡已填 {filled}/{len(rows)} → {jpath}')
    print(f'   索引 → {out / "01_章节索引.md"}')


if __name__ == '__main__':
    main()
