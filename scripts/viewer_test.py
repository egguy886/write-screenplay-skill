"""新观众测试（剧本规范 v2 · 门禁一）：只给观众“看得到、听得到”的东西，让没读过小说的读者复述、指出看不懂的地方、打分。

用法：python3 scripts/viewer_test.py --recap "上集结尾观众看到的" 剧本1.md [剧本2.md ...] --out review/看懂测试/xxx.json
  · 多个剧本按顺序当连续几集给（后一集的“前情”就是前一集）。
  · 自动去掉：信息区（> 开头）、拍表（| 开头）、中文潜台词、改动说明——这些观众看不到。
  · 模型固定 gpt-6-luna + max（CODEX_MODEL / CODEX_EFFORT 可覆盖），只读沙箱。
"""
import argparse, json, os, re, subprocess, sys

def resolve_codex_bin():                       # 用 ChatGPT.app 自带的 codex（PATH 里的旧版 codex 不认 gpt-6-*）
    if os.environ.get('CODEX_BIN') and os.path.exists(os.environ['CODEX_BIN']):
        return os.environ['CODEX_BIN']
    mac = '/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex'
    return mac if os.path.exists(mac) else 'codex'

def viewable(path):
    out = []; screen = False
    for l in open(path, encoding='utf-8'):
        s = l.rstrip('\n')
        if s.startswith('【屏幕'): screen = True; out.append(s); continue
        if screen and s.startswith('>'): out.append('[on-screen text] ' + s.lstrip('> ')); continue   # 屏幕/短信文字观众看得到，保留
        screen = False
        if s.startswith(('>', '|', '<!--')) or s.startswith('（中文潜台词') or s.startswith('**核心道具') or s.startswith('**冲突') \
           or s.startswith('**造型') or s.startswith('**陈设') or s.startswith('**出场人物') or s.startswith('**【Episode'):
            continue
        s = re.sub(r'（后期叠字：([^）]*)）', r'[on-screen text: \1]', s)
        out.append(s)
    t = re.sub(r'\n{3,}', '\n\n', '\n'.join(out)).strip().replace('（v2）', '')
    return t

PROMPT = """You are a typical viewer of English-language vertical short dramas (ReelShort / DramaBox) watching on a phone. You have NOT read the source novel. Below is exactly what appears on screen and what is heard, episode by episode (action lines are in Chinese and describe only what the camera shows; dialogue is English). Flashbacks marked "复用 E.. 镜头" reuse footage the viewer has already seen in that earlier episode.

What the viewer remembers from just before these episodes:
{recap}

{eps}

For EACH episode, answer as that viewer, honestly, without guessing beyond what is on screen:
- retell: what happened, in 2-3 plain sentences
- confusions: list every moment where you did not understand WHAT happened, WHY someone did something, or WHAT an object/line meant (quote the moment). Empty list if none.
- want_next: what you want to know in the next episode (one sentence), or "nothing" if the ending did not make you curious
- clarity: 1-10 (10 = understood everything)
- engagement: 1-10 (10 = must watch next)

Reply with JSON only: {{"episodes":[{{"title":"...","retell":"...","confusions":["..."],"want_next":"...","clarity":0,"engagement":0}}]}}"""

if __name__ != '__main__':
    raise SystemExit
ap = argparse.ArgumentParser(); ap.add_argument('scripts', nargs='+'); ap.add_argument('--recap', required=True); ap.add_argument('--out', required=True)
a = ap.parse_args()
eps = '\n\n'.join(f'===== EPISODE {i+1} =====\n{viewable(p)}' for i, p in enumerate(a.scripts))
os.makedirs(os.path.dirname(a.out) or '.', exist_ok=True)
last = a.out + '.last.txt'
cmd = [resolve_codex_bin(), 'exec', '-m', os.environ.get('CODEX_MODEL', 'gpt-6-luna'), '-c', 'model_reasoning_effort="' + os.environ.get('CODEX_EFFORT', 'max') + '"',
       '--skip-git-repo-check', '-s', 'read-only', '-o', last, PROMPT.format(recap=a.recap, eps=eps)]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
txt = open(last, encoding='utf-8').read() if os.path.exists(last) else r.stdout
m = re.search(r'\{.*\}', txt, re.S)
if not m:
    sys.exit(f'没拿到结果：{r.stderr[-400:]}')
d = json.loads(m.group(0)); d['scripts'] = a.scripts
json.dump(d, open(a.out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for e, p in zip(d['episodes'], a.scripts):
    print(f"{os.path.basename(p)}  看懂 {e['clarity']}  想追 {e['engagement']}  看不懂 {len(e['confusions'])} 处")
