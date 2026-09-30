"""버튼 안내 바(칩 안의 흰 글자): 칩 검출 → 글자 구간 검출 → 세로 그라데이션 배경 복원 → 한글.
translation/img/help.json: {"<key>": {"<칩번호>": "번역", ...}}   (칩 번호는 검출 시트 참고)"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, assets, lines
ST = dict(font='H', size=17, fill=[248, 248, 248], strokes=[[2, [16, 22, 40]]], align='l', squeeze=0.62)

def white(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (a[..., 3] > 200) & (r > 215) & (g > 215) & (b > 215)

def chips(a):
    """(행 y0,y1, x0,x1) 불투명 칩 목록."""
    op = a[..., 3] > 200
    out = []
    for y0, y1 in lines.runs(op.mean(1) > 0.02):
        if y1 - y0 < 10: continue
        cols = op[y0:y1].mean(0) > 0.5
        for x0, x1 in lines.runs(cols):
            if x1 - x0 >= 12: out.append((y0, y1, x0, x1))
    return out

def text_span(a, c):
    """흰 열 구간: 간격 2 이하 병합 후, 폭 10 이상인 첫 구간부터 끝까지 (짧은 구간 = 아이콘 반사광)."""
    y0, y1, x0, x1 = c
    w = white(a[y0:y1, x0:x1]).any(0)
    m = []
    for s_, e_ in lines.runs(w):
        if m and s_ - m[-1][1] <= 2: m[-1] = (m[-1][0], e_)
        else: m.append((s_, e_))
    big = [t for t in m if t[1] - t[0] >= 10]
    if not big: return None
    return x0 + big[0][0] - 1, x0 + m[-1][1] + 1

def detect(k):
    d, i, a = grp.load(k)
    res = []
    for c in chips(a):
        sp = text_span(a, c)
        if sp: res.append((c, sp))
    return d, i, a, res

def sheet(keys):
    outs = []
    for k in keys:
        d, i, a, res = detect(k)
        bx = [(s, c[0], e, c[1]) for c, (s, e) in res]
        p = os.path.join(grp.SHEETS, 'help_%s.png' % assets.safe(k)); outs.append(p)
        h = max(c[1] for c, _ in res) + 2
        grp.sheet(k, a, bx, p, scale=2, crop=(0, 0, a.shape[1], h))
    return outs

def run(keys=None):
    tr = json.load(open(os.path.join(grp.TR, 'help.json'), encoding='utf-8'))
    outs = []
    for k, m in tr.items():
        if keys and k not in keys: continue
        d, i, a, res = detect(k)
        b = a.copy()
        for n, t in m.items():
            if n.startswith('_'): continue
            (y0, y1, cx0, cx1), (s, e) = res[int(n)]
            e2 = cx1 - 2 if m.get('_toend', 1) else e
            # 배경: 글자 구간 오른쪽 칩 안쪽 열(글자 없는 곳)의 세로 그라데이션
            wcols = white(a[y0:y1, cx0:cx1]).any(0)
            clean = [x for x in range(cx0 + 2, cx1 - 2) if not wcols[x - cx0]]
            cand = [x for x in clean if x > e] or clean
            ref = np.median(a[y0:y1, cand[len(cand) // 3:len(cand) * 2 // 3 + 1]], 1)
            b[y0:y1, s:e2] = ref[:, None]
            render.draw(b, t, (s - 1, y0 + 2, e2, y1 - 2), dict(ST, **m.get('_st', {})))
        nd = grp.write(k, d, b)
        for extra in m.get('_also', []):
            open(os.path.join(grp.PATCHED, assets.safe(extra) + '.pom'), 'wb').write(nd)
        h = max(c[1] for c, _ in res) + 2
        grp.preview(k, nd, crop=(0, 0, a.shape[1], h), scale=2)
        outs.append(os.path.join(grp.PREVIEW, assets.safe(k) + '.png'))
    grp.contact(outs, os.path.join(grp.ROOT, 'work', 'pv_help.png'), cols=1)

KEYS = ['2749', '2936', '2942', '2744', '2764', '2933', 'fum:pom/select/help_bar.pom', 'fum:pom/castom/c_help_bar.pom']
if __name__ == '__main__':
    if sys.argv[1:] == ['sheet']:
        o = sheet(KEYS); grp.contact(o, os.path.join(grp.ROOT, 'work', 'v_helpsheet.png'), cols=1)
    else:
        run(sys.argv[1:] or None)
