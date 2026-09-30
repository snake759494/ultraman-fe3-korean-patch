"""필살기 목록 *_h (항목 2894~2932, FUM select/wazamei 사본 동일). 흰 글자(16단계 알파), 14px 줄 간격."""
import sys, os, json, re
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, assets
KEYS = [str(k) for k in range(2894, 2933)]
ST = dict(font='EB', size=13, fill=[230, 230, 230], align='l', valign='m', squeeze=0.62, cap=10.4)

def line_boxes(a, P=14):
    """14px 고정 칸: 잉크가 있는 칸마다 (x0, 칸 위, x1, 칸 위+13)."""
    m = a[..., 3] > 60
    out = []
    for s in range(0, a.shape[0] // P):
        sub = m[s * P:s * P + P]
        if sub.sum() < 6: continue
        cols = np.nonzero(sub.any(0))[0]
        out.append((int(cols.min()), s * P, int(cols.max()) + 1, s * P + 13))
    return out

def sheets():
    for k in KEYS:
        d, i, a = grp.load(k)
        bx = line_boxes(a)
        x1 = max(b[2] for b in bx) + 4; y1 = max(b[3] for b in bx) + 4
        grp.sheet(k, a, bx, os.path.join(grp.SHEETS, 'ml_%s.png' % k), scale=3, crop=(0, 0, min(256, x1 + 30), y1))
        print(k, len(bx))

def fum_names():
    """단독 키 → 같은 내용의 FUM 멤버 이름."""
    out = {}
    for n in assets.fum_index():
        if n.startswith('pom/select/wazamei/'):
            data = assets.get('fum:' + n)
            for k in KEYS:
                if assets.get(k) == data: out.setdefault(k, []).append(n)
    return out

def run():
    tr = json.load(open(os.path.join(grp.TR, 'movelist.json'), encoding='utf-8'))
    fn = fum_names()
    outs = []
    for k in KEYS:
        d, i, a = grp.load(k)
        bx = line_boxes(a)
        ko = tr[k]
        assert len(ko) == len(bx), (k, len(ko), len(bx))
        b = a.copy(); b[..., 3] = 0
        for (x0, y0, x1, y1), s in zip(bx, ko):
            render.draw(b, s, (1, y0, max(x1 + 2, 60), y0 + 13), ST)
        nd = grp.write(k, d, b)
        for n in fn.get(k, []):
            open(os.path.join(grp.PATCHED, assets.safe('fum:' + n) + '.pom'), 'wb').write(nd)
        grp.preview(k, nd, crop=(0, 0, 200, 14 * len(bx) + 2), scale=2, bgcol=(20, 20, 40, 255))
        outs.append(os.path.join(grp.PREVIEW, k + '.png'))
    for j in range(0, len(outs), 12):
        grp.contact(outs[j:j + 12], os.path.join(grp.ROOT, 'work', 'pv_ml%d.png' % (j // 12)), cols=4)

if __name__ == '__main__':
    sheets() if sys.argv[1:] == ['sheet'] else run()
