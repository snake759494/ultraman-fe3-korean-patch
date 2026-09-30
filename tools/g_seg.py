"""투명 배경 흰 글자 목록(여러 메시지가 한 줄에 붙은 그림): 줄 → 조각(간격 gap 이상) 검출, 조각마다 교체.
translation/img/seg.json {key: {"gap": 9, "st": {...}, "tr": {"행.조각": "번역" | null(그대로)}, "also": []}}"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, assets, lines
BASE = dict(font='B', size=16, fill=[235, 235, 235], strokes=[[1, [20, 20, 20]]], align='l', squeeze=0.55)

def segs(a, gap=9, thr=60):
    m = a[..., 3] > thr
    out = []
    for r, (y0, y1) in enumerate([t for t in lines.runs(m.any(1)) if t[1] - t[0] >= 5]):
        cols = m[y0:y1].any(0); rr = []
        for s, e in lines.runs(cols):
            if rr and s - rr[-1][1] < gap: rr[-1] = (rr[-1][0], e)
            else: rr.append((s, e))
        out.append([(y0, y1, s, e) for s, e in rr])
    return out

def sheet(k, gap):
    d, i, a = grp.load(k)
    bx = []; lab = []
    for r, row in enumerate(segs(a, gap)):
        for c, (y0, y1, s, e) in enumerate(row): bx.append((s, y0, e, y1))
    grp.sheet(k, a, bx, os.path.join(grp.ROOT, 'work', 'segsheet.png'), scale=2)
    return segs(a, gap)

def run(only=None):
    spec = json.load(open(os.path.join(grp.TR, 'seg.json'), encoding='utf-8'))
    outs = []
    for k, s in spec.items():
        if only and k not in only: continue
        d, i, a = grp.load(k); b = a.copy()
        S = segs(a, s.get('gap', 9))
        st = dict(BASE, **s.get('st', {}))
        for key, t in s['tr'].items():
            if t is None: continue
            r, c = map(int, key.split('.'))
            y0, y1, x0, x1 = S[r][c]
            nx1 = S[r][c + 1][2] - 4 if c + 1 < len(S[r]) else min(a.shape[1], x1 + s.get('grow', 0))
            nx1 = max(x1, min(nx1, x1 + s.get('grow', 0)))
            b[y0 - 1:y1 + 1, x0:x1 + 1, 3] = 0
            render.draw(b, t, (x0, y0, nx1, y1), st)
        nd = grp.write(k, d, b)
        for e in s.get('also', []): open(os.path.join(grp.PATCHED, assets.safe(e) + '.pom'), 'wb').write(nd)
        grp.preview(k, nd, scale=2, bgcol=(30, 30, 60, 255)); outs.append(os.path.join(grp.PREVIEW, assets.safe(k) + '.png'))
    return outs

if __name__ == '__main__':
    if sys.argv[1] == 'sheet':
        for r, row in enumerate(sheet(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 9)): print(r, [(c, x0, x1) for c, (y0, y1, x0, x1) in enumerate(row)])
    else:
        o = run(sys.argv[1:] or None); grp.contact(o, os.path.join(grp.ROOT, 'work', 'pv_seg.png'), cols=1)
