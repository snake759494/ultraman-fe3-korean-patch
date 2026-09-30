"""대전 HUD 캐릭터 이름 (FUM pom/game_2d/c_*_pom.ENC, 128×128 위쪽 0~20행)."""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, assets
ST = dict(font='H', size=16, fill={'v': [[150, 150, 150], [214, 214, 214]]}, strokes=[[2, [0, 0, 0]]], align='l', squeeze=0.55)

def run():
    tr = json.load(open(os.path.join(grp.TR, 'hudname.json'), encoding='utf-8'))
    outs = []
    for k, name in tr.items():
        key = 'fum:pom/game_2d/c_%s_pom.ENC' % k
        d, i, a = grp.load(key)
        b = a.copy()
        m = a[:21, :, 3] > 0
        x1 = int(np.nonzero(m.any(0))[0].max()) + 1
        b[:21, :, 3] = 0
        render.draw(b, name, (1, 1, min(126, x1), 17), dict(ST, squeeze=0.4))
        nd = grp.write(key, d, b)
        grp.preview(key, nd, crop=(0, 0, 128, 24), scale=2)
        outs.append(os.path.join(grp.PREVIEW, assets.safe(key) + '.png'))
    grp.contact(outs, os.path.join(grp.ROOT, 'work', 'pv_hud.png'), cols=5)

if __name__ == '__main__':
    run()
