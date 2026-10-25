# -*- coding: utf-8 -*-
"""长篇改编脚本共用的小工具：章节区间解析与格式化。"""


def parse_ranges(spec):
    """'1-3,5,8-9' / [1, '4-6'] / 7 -> [1, 2, 3, 5, 8, 9]"""
    if spec is None or spec == '':
        return []
    if isinstance(spec, int):
        return [spec]
    if isinstance(spec, list):
        out = []
        for s in spec:
            out += parse_ranges(s)
        return sorted(set(out))
    out = set()
    for part in str(spec).replace('，', ',').split(','):
        part = part.strip().lower().replace('ch', '')
        if not part:
            continue
        if '-' in part or '–' in part:
            lo, hi = part.replace('–', '-').split('-', 1)
            lo, hi = int(lo), int(hi)
            out.update(range(min(lo, hi), max(lo, hi) + 1))
        else:
            out.add(int(part))
    return sorted(out)


def fmt_ranges(nums):
    nums = sorted(set(nums))
    if not nums:
        return '—'
    out, start, prev = [], nums[0], nums[0]
    for n in nums[1:] + [None]:
        if n is not None and n == prev + 1:
            prev = n
            continue
        out.append(f'{start}' if start == prev else f'{start}-{prev}')
        if n is not None:
            start = prev = n
    return ','.join(out)
