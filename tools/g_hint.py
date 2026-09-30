"""힌트 판(hint1~20, 항목 2624~2643): 16px 격자 배경을 오른쪽 빈 구간에서 복원 후 한글."""
import sys, json, os
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render
KEYS = [str(k) for k in range(2624, 2644)]
ST = dict(font='H', size=24, fill={'v': [[236, 244, 176], [214, 222, 150]]}, strokes=[[2, [32, 19, 6]]],
          align='l', valign='t', lead=24, squeeze=0.8)
LABEL = dict(font='EB', size=15, fill={'v': [[250, 250, 250], [190, 190, 190]]}, strokes=[[2, [40, 40, 40]]], align='l', valign='t', squeeze=1)

def periodic_bg(A, x0, x1, P, thr=36, it=3):
    """A(N×H×W×4): 행별·x위상별 중앙값 배경 (글자 픽셀 제외 반복)."""
    N, H, W, _ = A.shape
    xs = np.arange(W); ph = xs % P
    mask = np.zeros((N, H, W), bool)
    for _ in range(it):
        tpl = np.zeros((H, P, 4), np.float32)
        for p in range(P):
            cols = [x for x in range(x0, x1) if x % P == p]
            S = A[:, :, cols]; M = ~mask[:, :, cols]
            Sm = np.where(M[..., None], S, np.nan)
            v = np.nanmedian(Sm.transpose(1, 0, 2, 3).reshape(H, -1, 4), 1)
            tpl[:, p] = np.where(np.isnan(v), np.median(S.transpose(1, 0, 2, 3).reshape(H, -1, 4), 1), v)
        bg = tpl[:, ph]
        mask = np.abs(A - bg[None]).max(-1) > thr
        mask = np.stack([cv2.dilate(m.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) for m in mask])
    return bg

def run(keys=KEYS, show=False):
    tr = json.load(open(os.path.join(grp.TR, 'hint.json'), encoding='utf-8'))
    L = {k: grp.load(k) for k in KEYS}
    A = np.stack([L[k][2] for k in KEYS])
    bgT = periodic_bg(A, 40, 452, 16)
    outs = []
    for k in keys:
        d, i, a = L[k]
        diff = np.abs(a - bgT).max(-1)
        m = diff > 40; m[:29] = False; m[92:] = False; m[:, :31] = False; m[:, 455:] = False
        m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
        m[:29] = False; m[92:] = False; m[:, :31] = False; m[:, 455:] = False
        b = a.copy(); b[m] = bgT[m]
        # 'ヒント' 라벨 → '힌트': 라벨 영역(y 6..22, x 28..70)을 같은 행 96px 오른쪽으로 대체
        b[4:21, 28:84] = a[4:21, 28 + 112:84 + 112]
        render.draw(b, '힌트', (33, 5, 75, 20), LABEL)
        render.draw(b, tr[k], (33, 31, 468, 80), ST)
        nd = grp.write(k, d, b)
        grp.preview(k, nd)
        outs.append(os.path.join(grp.PREVIEW, k + '.png'))
    grp.contact(outs, os.path.join(grp.ROOT, 'work', 'pv_hint.png'), cols=2)

if __name__ == '__main__':
    run()
