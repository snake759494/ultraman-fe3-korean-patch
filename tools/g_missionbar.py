"""미션 평가 항목 misson_bar(2973, 2983~3002): 41px 막대, 흰 글자."""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, pom
ST = dict(font='EB', size=21, fill=[250, 250, 250], strokes=[[2, [4, 20, 90]]], align='l', squeeze=0.6)

def run():
    tr = json.load(open(os.path.join(grp.TR, 'missionbar.json'), encoding='utf-8'))
    outs = []
    global TPL
    TPL = grp.load('2983')[2]
    for k, rows in tr.items():
        d, i, a = grp.load(k)
        P = 41 if a.shape[0] == 512 else 40.5
        b = a.copy()
        tpl = TPL[10 * 41:11 * 41]
        if a.shape[0] == 512:
            for r in range(len(rows)): b[r * 41:(r + 1) * 41] = tpl
        else:  # 2973(512×128): 같은 막대 디자인 → 빈 막대로 채움
            for r in range(3): b[r * 41:min(128, (r + 1) * 41)] = tpl[:min(41, 128 - r * 41)]
        for r, s in enumerate(rows):
            y0 = int(r * P)
            render.draw(b, s, (7, y0 + 8, 500, y0 + 34), ST)
        nd = grp.write(k, d, b)
        grp.preview(k, nd, crop=(0, 0, 512, min(a.shape[0], 41 * max(4, len(rows)) + 4)))
        outs.append(os.path.join(grp.PREVIEW, k + '.png'))
    grp.contact(outs, os.path.join(grp.ROOT, 'work', 'pv_mb.png'), cols=4, scale=0.6)

if __name__ == '__main__':
    run()
