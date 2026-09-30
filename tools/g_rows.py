"""명시 구간 교체(투명 배경 흰 글자): translation/img/<name>.json {key: {"rows": [[y0,y1,[[x0,x1,"번역"],...]]], "st":{}, "also":[]}}"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, assets
BASE = dict(font='B', size=20, fill=[236, 236, 236], strokes=[[2, [60, 60, 60]]], align='l', squeeze=0.5)
def run(name):
    spec = json.load(open(os.path.join(grp.TR, name + '.json'), encoding='utf-8'))
    outs = []
    for k, s in spec.items():
        d, i, a = grp.load(k); b = a.copy()
        st = dict(BASE, **s.get('st', {}))
        for y0, y1, segs in s['rows']:
            kx = s.get('keep', {}).get(str(y0))
            if s.get('keep') is not None:
                b[max(0, y0 - 2):y1 + 2, :kx[0] if kx else None, 3] = 0
            for x0, x1, t in segs:
                if t is None: continue
                ink = __import__('numpy').nonzero((a[y0:y1, x0:x1, 3] > 60).any(0))[0]
                if len(ink): x1 = x0 + int(ink.max()) + 2   # 원문 폭까지만 표시됨
                b[max(0, y0 - 2):y1 + 2, x0:x1, 3] = 0
                render.draw(b, t, (x0 + 1, y0, x1 - 1, y1), st)
        nd = grp.write(k, d, b)
        for e in s.get('also', []): open(os.path.join(grp.PATCHED, assets.safe(e) + '.pom'), 'wb').write(nd)
        grp.preview(k, nd, bgcol=(30, 30, 60, 255)); outs.append(os.path.join(grp.PREVIEW, assets.safe(k) + '.png'))
    grp.contact(outs, os.path.join(grp.ROOT, 'work', 'pv_rows.png'), cols=2)
if __name__ == '__main__':
    run(sys.argv[1])
