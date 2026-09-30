"""튜토리얼 말풍선(3005~3017): 흰 글자+빨간 외곽. 버튼 아이콘은 두고 오른쪽에 한글."""
import sys, os, json
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, lines
ST = dict(font='H', size=26, fill=[250, 250, 250], strokes=[[4, [60, 0, 10]], [2, [215, 25, 35]]], align='c', squeeze=0.6)

def run():
    tr = json.load(open(os.path.join(grp.TR, 'burst.json'), encoding='utf-8'))
    outs = []
    for k, ko in tr.items():
        d, i, a = grp.load(k)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]; op = a[..., 3] > 200
        white = op & (r > 200) & (g > 200) & (b > 200)
        white[:, :60] = False; white[:, 450:] = False; white[:40] = False; white[215:] = False
        icon = op & (((r > 150) & (b > 90) & (g < 130) & (b > g + 30)) | ((b > 170) & (r < 160) & (b > r + 40)))
        icon = cv2.morphologyEx(icon.astype(np.uint8), cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)).astype(bool)
        n, lab, stt, _ = cv2.connectedComponentsWithStats(icon.astype(np.uint8))
        icons = [s for s in stt[1:] if s[4] > 60 and s[2] > 12]
        if k == '3015': icons = [np.array([104, 87, 34, 38, 999])]  # ○ 버튼
        if k == '3016': icons = [np.array([95, 105, 87, 32, 999])]  # L1+R1 버튼 그림
        rows = [(y0, y1) for y0, y1 in lines.runs(white.any(1)) if y1 - y0 >= 8]
        merged = []
        for y0, y1 in rows:
            if merged and y0 - merged[-1][1] <= 3: merged[-1] = (merged[-1][0], y1)
            else: merged.append((y0, y1))
        assert len(merged) == len(ko), (k, merged)
        red = op & (r > g + 35) & (r > 50)
        red[:, :60] = False; red[:, 450:] = False; red[:40] = False; red[215:] = False
        er = cv2.dilate((white | red).astype(np.uint8), np.ones((15, 15), np.uint8)).astype(bool)
        for s in icons: er[s[1] - 1:s[1] + s[3] + 1, s[0] - 1:s[0] + s[2] + 1] = False
        u8 = np.ascontiguousarray(a[..., :3].astype(np.uint8))
        b2 = a.copy(); b2[..., :3] = cv2.inpaint(u8, er.astype(np.uint8), 7, cv2.INPAINT_TELEA)
        for (y0, y1), t in zip(merged, ko):
            xs = np.nonzero(white[y0:y1].any(0))[0]; x0, x1 = int(xs.min()), int(xs.max()) + 1
            ic = [s for s in icons if s[1] < y1 and s[1] + s[3] > y0]
            if ic:
                s = ic[0]; box = (s[0] + s[2] + 3, y0 - 2, max(x1 + 20, 420), y1 + 2); st = dict(ST, align='l')
            else:
                c = (x0 + x1) / 2; hw = max((x1 - x0) / 2 + 20, 60)
                box = (int(max(95, c - hw)), y0 - 2, int(min(425, c + hw)), y1 + 2); st = ST
            render.draw(b2, t, box, dict(st, size=min(26, int((y1 - y0) * 1.15))))
        nd = grp.write(k, d, b2)
        grp.preview(k, nd, crop=(60, 20, 460, 230))
        outs.append(os.path.join(grp.PREVIEW, k + '.png'))
    grp.contact(outs, os.path.join(grp.ROOT, 'work', 'pv_burst.png'), cols=3)

if __name__ == '__main__':
    run()
