"""스토리 자막 zimaku1~8 (2644~2651): 줄마다 원래 글자 폭 안에 가운데 정렬."""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, lines
ST = dict(font='B', size=27, fill={'v': [[250, 250, 250], [200, 200, 200]]}, strokes=[[2, [5, 5, 5]]], align='c', squeeze=0.6)

def rows(a):
    rr = []
    for y0, y1 in lines.runs((a[..., 3] > 40).any(1)):
        while y1 - y0 > 40: rr.append((y0, y0 + 33)); y0 += 33
        rr.append((y0, y1))
    return rr

def run():
    tr = json.load(open(os.path.join(grp.TR, 'zimaku.json'), encoding='utf-8'))
    outs = []
    for k, ko in tr.items():
        d, i, a = grp.load(k)
        rr = rows(a); assert len(rr) == len(ko), (k, rr)
        b = a.copy()
        for (y0, y1), t in zip(rr, ko):
            if t is None: continue
            xs = np.nonzero((a[y0:y1, :, 3] > 40).any(0))[0]
            x0, x1 = int(xs.min()), int(xs.max()) + 1
            b[y0:y1, :, 3] = 0
            render.draw(b, t, (x0, y0 + 1, x1, y1 - 1), ST)
        nd = grp.write(k, d, b)
        grp.preview(k, nd, crop=(0, 0, 512, rr[-1][1] + 2), bgcol=(60, 80, 120, 255))
        outs.append(os.path.join(grp.PREVIEW, k + '.png'))
    grp.contact(outs, os.path.join(grp.ROOT, 'work', 'pv_zm.png'), cols=2)

if __name__ == '__main__':
    run()
