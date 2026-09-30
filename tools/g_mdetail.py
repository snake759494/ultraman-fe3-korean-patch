"""미션 설명판 misn_detail01~20 (항목 2564~2583)."""
import sys, os, json
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render
KEYS = [str(k) for k in range(2564, 2584)]

def textmask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    lum = (r + g + b) / 3
    m = ((r > 140) & (g > 140)) | ((lum < 26) & (b < 45)) | ((g > 150) & (b > 150) & (r > 60))
    m[:, :12] = False; m[:, 455:] = False; m[:10] = False; m[246:] = False
    return m

def prep():
    L = {k: grp.load(k) for k in KEYS}
    A = np.stack([L[k][2] for k in KEYS])
    M = np.stack([cv2.dilate(textmask(a).astype(np.uint8), np.ones((5, 5), np.uint8)).astype(bool) for a in A])
    S = np.where(M[..., None], np.nan, A)
    bg = np.nanmedian(S, 0)
    hole = np.isnan(bg[..., 0])
    bg = np.where(np.isnan(bg), 0, bg).astype(np.float32)
    if hole.any():
        u8 = bg.astype(np.uint8)
        bg[..., :3] = cv2.inpaint(np.ascontiguousarray(u8[..., :3]), hole.astype(np.uint8), 5, cv2.INPAINT_TELEA)
        bg[..., 3] = 255
    return L, M, bg, hole

if __name__ == '__main__' and sys.argv[1:] == ['sheet']:
    L, M, bg, hole = prep()
    print('구멍', hole.sum())
    from PIL import Image
    Image.fromarray(bg.astype(np.uint8)).save(os.path.join(grp.ROOT, 'work', 'bg_mdetail.png'))
    outs = []
    for k in KEYS:
        d, i, a = L[k]
        m = textmask(a)
        bx = grp.boxes(m, gap=2, minh=5)
        p = os.path.join(grp.SHEETS, 'md_%s.png' % k); grp.sheet(k, a, bx, p, scale=2, crop=(0, 0, 512, 256)); outs.append(p)
        print(k, bx)

TITLE = dict(font='H', size=38, italic=0.12, fill={'v': [[255, 255, 255], [196, 198, 204]]},
             strokes=[[4, [6, 12, 30]], [2, [40, 44, 56]]], squeeze=0.7)
LABEL = dict(font='EB', size=17, fill={'v': [[236, 238, 240], [200, 200, 204]]}, strokes=[[2, [5, 10, 19]]], align='l', squeeze=0.8)
WIN = dict(font='EB', size=19, fill={'v': [[247, 178, 84], [249, 236, 70]]}, strokes=[[2, [30, 18, 4]]], align='l', squeeze=0.66)
LOSE = dict(font='EB', size=19, fill={'v': [[114, 191, 238], [190, 238, 248]]}, strokes=[[2, [1, 20, 50]]], align='l', squeeze=0.66)

def rows_of(m, y0, y1):
    """y0..y1 에서 글자 행 구간 (붙은 행은 가장 얕은 곳에서 분할)."""
    prof = m[y0:y1].sum(1)
    out = []; s = None
    for y, v in enumerate(list(prof) + [0]):
        if v and s is None: s = y
        if not v and s is not None:
            if y - s >= 4: out.append([s + y0, y + y0])
            s = None
    res = []
    for a, b in out:
        while b - a > 25:
            seg = prof[a - y0 + 14:min(b - y0, a - y0 + 26)]
            cut = a + 14 + int(np.argmin(seg)); res.append([a, cut]); a = cut
        res.append([a, b])
    return res

def run():
    tr = json.load(open(os.path.join(grp.TR, 'mdetail.json'), encoding='utf-8'))
    L, M, bg, hole = prep()
    outs = []
    for k in KEYS:
        d, i, a = L[k]
        tm = textmask(a)
        b = a.copy(); mm = M[KEYS.index(k)]
        b[mm] = bg[mm]
        t = tr[k]['t']; rows = tr[k]['rows']
        # 제목
        if len(t) == 1:
            render.draw(b, t[0], (16, 30, 452, 76), dict(TITLE, align='c'))
        else:
            render.draw(b, t[0], (16, 11, 452, 55), dict(TITLE, align='l'))
            render.draw(b, t[1], (16, 55, 452, 97), dict(TITLE, align='r'))
        rr = rows_of(tm[:, 30:455], 97, 248)
        assert len(rr) == len(rows), (k, rr, rows)
        mode = None
        for (y0, y1), s in zip(rr, rows):
            if s in ('승리 조건', '패배 조건'):
                mode = WIN if s == '승리 조건' else LOSE
                render.draw(b, s, (35, y0, 116, y1 - 1), dict(LABEL, justify=1))
            else:
                render.draw(b, s, (33, y0, 452, y1), mode)
        nd = grp.write(k, d, b)
        grp.preview(k, nd, crop=(0, 0, 470, 256))
        outs.append(os.path.join(grp.PREVIEW, k + '.png'))
    for j in range(0, 20, 6):
        grp.contact(outs[j:j + 6], os.path.join(grp.ROOT, 'work', 'pv_md%d.png' % (j // 6)), cols=2)

if __name__ == '__main__' and not sys.argv[1:]:
    run()
