"""커스텀 기술 설명 castom/wazasetumei/*_w?_pom.ENC (256×256, 64px 칸 4개). '!' 노란 줄, '~' 하늘색 줄."""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, assets
COL = {'': [240, 240, 240], '!': [255, 255, 0], '~': [60, 230, 255]}
def run():
    W = json.load(open(os.path.join(grp.TR, 'waza.json'), encoding='utf-8'))
    outs = []
    for n, blocks in W.items():
        key = 'fum:pom/castom/wazasetumei/%s_pom.ENC' % n
        d, i, a = grp.load(key); b = a.copy()
        small = a[..., 3].mean() > 200  # 검은 불투명 배경 = 작은 글자 판
        size, lead = (13, 15) if small else (17, 19)
        for k, lines_ in enumerate(blocks):
            y0 = 64 * k
            reg = a[y0:y0 + 64].reshape(-1, 4)
            bgc = np.median(reg, 0)
            b[y0:y0 + 64] = bgc
            for j, t in enumerate(lines_):
                c = t[0] if t[:1] in ('!', '~') else ''
                t = t[len(c):]
                yy = y0 + 2 + j * lead
                render.draw(b, t, (1, yy, 255, yy + lead), dict(font='EB' if not small else 'B', size=size, fill=COL[c],
                            strokes=[[1, [20, 20, 20]]] if not small else [], align='l', squeeze=0.55))
        grp.write(key, d, b)
        nd = open(os.path.join(grp.PATCHED, assets.safe(key) + '.pom'), 'rb').read()
        grp.preview(key, nd, bgcol=(30, 0, 40, 255)); outs.append(os.path.join(grp.PREVIEW, assets.safe(key) + '.png'))
    grp.contact(outs[:12], os.path.join(grp.ROOT, 'work', 'pv_waza.png'), cols=4)
if __name__ == '__main__':
    run()
