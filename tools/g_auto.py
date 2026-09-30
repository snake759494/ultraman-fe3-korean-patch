"""행 자동 검출 목록: translation/img/auto.json {key: {"items": [..행 순서..], "st": {}, "align": "l|c", "also": [], "gap": 0, "x": [x0,x1]}}
null 은 그대로 둠. 행 전체(지정 x 범위)를 투명하게 지우고 다시 그림."""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, assets, lines
BASE = dict(font='B', size=16, fill=[240, 240, 240], align='l', squeeze=0.5)
def rows(a, gap=0, x=None, thr=60, lum=False):
    m = (a[..., :3].max(-1) > 120) if lum else (a[..., 3] > thr)
    if x: m[:, :x[0]] = False; m[:, x[1]:] = False
    rr = []
    for s, e in lines.runs(m.any(1)):
        if rr and s - rr[-1][1] <= gap: rr[-1] = (rr[-1][0], e)
        else: rr.append((s, e))
    return [(s, e) for s, e in rr if e - s >= 4]
def show(k, gap=0, x=None):
    d, i, a = grp.load(k); rr = rows(a, gap, x, lum=True); print(k, len(rr), rr)
def run(only=None):
    spec = json.load(open(os.path.join(grp.TR, 'auto.json'), encoding='utf-8'))
    outs = []
    for k, s in spec.items():
        if only and k not in only: continue
        d, i, a = grp.load(k); b = a.copy()
        x = s.get('x'); rr = rows(a, s.get('gap', 0), x, lum=s.get('lum', False) or s.get('detect') == 'lum')
        assert len(rr) == len(s['items']), (k, len(rr), len(s['items']))
        X0, X1 = x if x else (0, a.shape[1])
        st = dict(BASE, **s.get('st', {}))
        for (y0, y1), t in zip(rr, s['items']):
            if t is None: continue
            stt = dict(st)
            if s.get('autocolor'):
                sub = a[y0:y1, X0:X1].reshape(-1, 4); sub = sub[sub[:, 3] > 200]
                sat = sub[:, :3].max(1) - sub[:, :3].min(1); stt['fill'] = np.median(sub[sat >= np.percentile(sat, 70), :3], 0).tolist()
            if s.get('lum'): b[max(0, y0 - 1):y1 + 2, X0:X1, :3] = s.get('bgc', [0, 0, 0])
            else: b[y0:y1, X0:X1, 3] = 0
            if isinstance(t, list):
                for n_, (xx, tt) in enumerate(t):
                    nx = t[n_ + 1][0] - 4 if n_ + 1 < len(t) else X1 - 1
                    render.draw(b, tt, (X0 + xx + 1, y0, X0 + nx, y1), stt)
            else: render.draw(b, t, (X0 + 1, y0, X1 - 1, y1), stt)
        nd = grp.write(k, d, b)
        for e in s.get('also', []): open(os.path.join(grp.PATCHED, assets.safe(e) + '.pom'), 'wb').write(nd)
        grp.preview(k, nd, bgcol=(60, 30, 70, 255), scale=2); outs.append(os.path.join(grp.PREVIEW, assets.safe(k) + '.png'))
    grp.contact(outs, os.path.join(grp.ROOT, 'work', 'pv_auto.png'), cols=len(outs))
if __name__ == '__main__':
    if sys.argv[1:2] == ['show']: show(sys.argv[2], int(sys.argv[3]) if len(sys.argv) > 3 else 0)
    else: run(sys.argv[1:])
