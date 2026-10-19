"""타이틀 메뉴(2751, 4bpp, 팔레트 2개: 0=평상시, 1=선택 시).
두 양식으로 각각 렌더한 뒤, 두 팔레트에서의 오차 합이 가장 작은 번호를 고른다(선택 시 글자 깨짐 방지)."""
import sys, os
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, pom, imgedit
KEY = '2751'; ROLL = -223; TIDX = 7
KO = {0: '울트라 모드', 1: '배틀 모드', 2: 'VS 모드', 3: '커스텀 모드', 4: '프랙티스 모드', 5: '튜토리얼',
      6: '뷰 모드', 7: '리플레이 모드', 8: '옵션', 11: '태그 모드'}
BASE = dict(font='H', size=17, italic=0.22, align='l', squeeze=0.7)
ST = [dict(BASE, fill={'h': [[252, 252, 252], [143, 148, 150]]}, strokes=[[3, [0, 146, 195]], [2, [2, 46, 61]]]),
      dict(BASE, fill={'h': [[252, 252, 252], [235, 221, 211]]}, strokes=[[3, [223, 8, 10]], [2, [128, 25, 32]]])]

def feat(c):
    a = c[..., 3:4] / 255.0
    return np.concatenate([c[..., :3] * a, c[..., 3:4] * 1.2], -1)

def run():
    d = grp.assets.get(KEY); i = pom.info(d)
    idx = np.roll(pom.indices(d, i), ROLL, 1)
    pals = [imgedit.pal_disp(d, i, n) for n in (0, 1)]
    for k, t in KO.items():
        y0, y1 = 24 * k, 24 * k + 22
        cols = np.nonzero((idx[y0:y1, :200] != TIDX).any(0))[0]
        x1 = int(cols.max()) + 1
        H, W = 24, idx.shape[1]
        tg = []
        for st in ST:
            c = np.zeros((H, W, 4), np.float32)
            render.draw(c, t, (1, 0, x1, 22), st)
            tg.append(c)
        # 두 팔레트 동시 오차
        F0 = feat(tg[0]).reshape(-1, 4); F1 = feat(tg[1]).reshape(-1, 4)
        P0 = feat(pals[0]); P1 = feat(pals[1])
        err = ((F0[:, None] - P0[None]) ** 2).sum(-1) * 2 + ((F1[:, None] - P1[None]) ** 2).sum(-1)
        best = err.argmin(1).reshape(H, W)
        best[(tg[0][..., 3] < 20) & (tg[1][..., 3] < 20)] = TIDX
        idx[y0:y0 + 24] = best
    nd = pom.set_indices(d, i, np.roll(idx, -ROLL, 1))
    open(os.path.join(grp.PATCHED, KEY + '.pom'), 'wb').write(nd)
    from PIL import Image
    ims = []
    for n in (0, 1):
        a = np.roll(pom.rgba(nd, n), ROLL, 1)[:290, :180]
        im = Image.fromarray(a); bg = Image.new('RGBA', im.size, (60, 60, 140, 255)); bg.alpha_composite(im)
        ims.append(bg.convert('RGB').resize((360, 580), Image.NEAREST))
    c = Image.new('RGB', (720, 580)); c.paste(ims[0], (0, 0)); c.paste(ims[1], (360, 0))
    c.save(os.path.join(grp.ROOT, 'work', 'pv_menu.png'))

if __name__ == '__main__':
    run()
