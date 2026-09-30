"""해금 알림 common_c(3096~3193): 감싸 저장된 3줄 상자. 상자를 펼쳐 글자만 지우고 한글 3줄."""
import sys, os, json
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, lines
KEYS = [str(k) for k in range(3096, 3194)]
ST = dict(font='EB', size=20, fill=[250, 250, 250], glow=[2, [30, 110, 255], 1.2, 1.4], align='c', squeeze=0.6)

def unroll(a):
    op = (a[..., 3] > 200).sum(0) > 30
    gaps = [(s, e) for s, e in lines.runs(~op)]
    s, e = max(gaps, key=lambda t: t[1] - t[0])
    R = a.shape[1] - e  # 빈 구간이 오른쪽 끝으로
    return R

def box(a):
    op = a[..., 3] > 200
    ys = lines.runs(op.sum(1) > 30); xs = lines.runs(op.sum(0) > 30)
    return max(xs, key=lambda t: t[1] - t[0]), max(ys, key=lambda t: t[1] - t[0])

def rows(a, bx):
    (x0, x1), (y0, y1) = bx
    w = (a[y0:y1, x0 + 4:x1 - 4, :3].min(-1) > 200)
    rr = [(s + y0, e + y0) for s, e in lines.runs(w.any(1)) if e - s >= 5]
    return rr

def sheet():
    ims = []
    for k in KEYS:
        d, i, a = grp.load(k); R = unroll(a); a = np.roll(a, R, 1)
        (x0, x1), (y0, y1) = box(a)
        rr = rows(a, box(a))
        if len(rr) < 3: print('rows', k, rr)
        y = rr[1] if len(rr) > 1 else (y0, y1)
        im = Image.fromarray(a[y[0] - 2:y[1] + 2, x0:x1].astype(np.uint8)).convert('RGB')
        c = Image.new('RGB', (300, 26)); c.paste(im, (40, 2)); ImageDraw.Draw(c).text((2, 6), k, fill=(255, 255, 0))
        ims.append(c)
    for j in range(0, len(ims), 25):
        s = Image.new('RGB', (600, 26 * 13))
        for n, im in enumerate(ims[j:j + 25]): s.paste(im, ((n // 13) * 300, (n % 13) * 26))
        s = s.resize((1200, 26 * 13 * 2)); s.save(os.path.join(grp.ROOT, 'work', 'nt_%d.png' % (j // 25)))

def run():
    tr = json.load(open(os.path.join(grp.TR, 'notice.json'), encoding='utf-8'))
    outs = []
    for k in KEYS:
        d, i, a = grp.load(k); R = unroll(a); a = np.roll(a, R, 1); b = a.copy()
        (x0, x1), (y0, y1) = box(a)
        if k not in tr: continue
        l1, l2 = tr[k]
        sub = a[y0 + 4:y1 - 4, x0 + 4:x1 - 4]
        dark = sub[sub[..., :3].max(-1) < 30]
        col = np.median(dark, 0) if len(dark) else np.array([4, 4, 12, 254.])
        b[y0 + 4:y1 - 4, x0 + 4:x1 - 4] = col
        H = (y1 - y0 - 8) / 3
        for j, t in enumerate([l1, l2, '출현했습니다!']):
            render.draw(b, t, (x0 + 7, int(y0 + 4 + H * j), x1 - 7, int(y0 + 4 + H * (j + 1))), ST)
        nd = grp.write(k, d, np.roll(b, -R, 1))
        pv = os.path.join(grp.PREVIEW, k + '.png')
        im = Image.fromarray(np.roll(grp.imgedit.load(nd)[1], R, 1).astype(np.uint8)); bg = Image.new('RGBA', im.size, (40, 0, 40, 255)); bg.alpha_composite(im)
        bg.convert('RGB').crop((x0, y0, x1, y1)).save(pv); outs.append(pv)
    grp.contact(outs, os.path.join(grp.ROOT, 'work', 'pv_nt.png'), cols=6)

if __name__ == '__main__':
    sheet() if sys.argv[1:] == ['sheet'] else run()
