"""커스텀 타입 목록(2807 = FUM select/costom_s.pom, 4bpp 팔레트 6개)의 왼쪽 라벨 16줄.
g_boxes.py 가 만든 결과(커스텀 1~4 칩) 위에 덧그린다 → g_boxes.py 다음에 실행.
라벨 칩 바탕은 글자가 없는 다른 줄의 같은 열을 가져와 복원한다(일본어 잔재·바탕색 변질 방지)."""
import sys, os
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, pom, imgedit, assets
KEYS = ['2807', 'fum:pom/select/costom_s.pom']
ROLL = 12; P = 16; X1 = 104
N = ["멀티 타입", "파워 타입", "스카이 타입", "플래시 타입", "미라클 타입", "스트롱 타입", "루나 모드", "이클립스 모드",
     "퓨처 모드", "V2", "슈프림 버전", "스탠더드", "크래셔", "강화", "냉기", "화염"]
ST = dict(font='H', size=14, fill={'v': [[60, 200, 255], [20, 60, 230]]}, strokes=[[1, [230, 240, 255]]], align='c', squeeze=0.6)

def ink(sub):
    m = ((sub[..., 2] - sub[..., 0]) > 50) & (sub[..., 3] > 100) & (sub[..., 2] > 150)
    return cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool)

def run():
    for key in KEYS:
        d = assets.get(key); i = pom.info(d)
        orig = np.roll(pom.rgba(d, 0).astype(np.float32), ROLL, 1)
        base_p = os.path.join(grp.PATCHED, assets.safe(key) + '.pom')
        cur = open(base_p, 'rb').read() if os.path.exists(base_p) else d
        b = np.roll(pom.rgba(cur, 0).astype(np.float32), ROLL, 1)
        inks = [ink(orig[r * P:r * P + P, :X1]) for r in range(16)]
        for r in range(16):
            y0 = r * P
            for x in range(X1):
                if not inks[r][:, x].any(): continue
                donors = [q for q in (14, 15, 9, 13, 6, 0) if not inks[q][:, x].any()]
                if donors: b[y0:y0 + P, x] = orig[donors[0] * P:donors[0] * P + P, x]
                else:  # 가운데: 화염 줄의 글자 없는 가까운 열(바탕은 가운데가 거의 균일)
                    xx = 42 if x < 53 else 64
                    b[y0:y0 + P, x] = orig[15 * P:15 * P + P, xx]
            render.draw(b, N[r], (8, y0 + 1, 96, y0 + 15), ST)
        W = b.shape[1]
        regs = []
        for r in range(16):
            for x0, x1 in ((0, X1),):
                xs = [(x - ROLL) % W for x in (x0, x1 - 1)]
                if xs[0] <= xs[1]: regs.append((xs[0], r * P, xs[1] + 1, r * P + P))
                else: regs += [(xs[0], r * P, W, r * P + P), (0, r * P, xs[1] + 1, r * P + P)]
        # 칩 바탕 픽셀은 원래 번호를 그대로 쓴다(다중 팔레트 보존)
        nd = imgedit.save(cur, np.roll(b, -ROLL, 1), None, 0, regs)
        open(base_p, 'wb').write(nd)
    from PIL import Image
    ims = []
    for n in (0, 4):
        a = np.roll(pom.rgba(nd, n), ROLL, 1)[:, :110]
        im = Image.fromarray(a); bg = Image.new('RGBA', im.size, (0, 0, 0, 255)); bg.alpha_composite(im)
        ims.append(bg.convert('RGB').resize((330, 768), Image.NEAREST))
    c = Image.new('RGB', (660, 768)); c.paste(ims[0], (0, 0)); c.paste(ims[1], (330, 0))
    c.save(os.path.join(grp.ROOT, 'work', 'pv_custom.png'))

if __name__ == '__main__':
    run()
