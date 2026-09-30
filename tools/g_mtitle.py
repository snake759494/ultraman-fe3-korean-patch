"""미션 제목 misn_title01~20 (항목 2584~2603). 넘친 조각 자리는 비우고, 각 줄을 원래 시작점부터 512px 안에."""
import sys, os, json
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render
KEYS = [str(k) for k in range(2584, 2604)]
ST = dict(font='H', size=66, fill={'v': [[255, 255, 255], [236, 240, 248]]}, strokes=[[6, [18, 78, 160]]],
          glow=[8, [60, 140, 250], 3.0, 1.1], align='l', squeeze=0.62)

OVERRIDE = {'2589': ['마그마 성인을', '격퇴하라!']}

def run():
    tr = json.load(open(os.path.join(grp.TR, 'mdetail.json'), encoding='utf-8'))
    outs = []
    for k, dk in zip(KEYS, [str(int(k) - 20) for k in KEYS]):
        d, i, a = grp.load(k)
        m = (a[..., :3].max(-1) > 30).astype(np.uint8)
        n, lab, stats, cent = cv2.connectedComponentsWithStats(m)
        mains = sorted([s for s in stats[1:] if s[4] > 3000 and s[3] >= 60 and s[1] < 240], key=lambda s: s[1])
        t = OVERRIDE.get(k, tr[dk]['t'])
        assert len(mains) == len(t), (k, mains, t)
        b = a.copy(); b[..., :3] = 0; b[..., 3] = 255
        for s, line in zip(mains, t):
            x0, y0, w, h = s[:4]
            render.draw(b, line, (x0 + 10, y0 + 12, 506, y0 + h - 12), ST)
        nd = grp.write(k, d, b)
        grp.preview(k, nd)
        outs.append(os.path.join(grp.PREVIEW, k + '.png'))
    for j in range(0, 20, 8):
        grp.contact(outs[j:j + 8], os.path.join(grp.ROOT, 'work', 'pv_mt%d.png' % (j // 8)), cols=4, scale=0.5)

if __name__ == '__main__':
    run()
