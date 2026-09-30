"""튜토리얼 대사(2753~2759): 행마다 오른쪽 끝에서 시작해 감싸 저장된 한 줄. roll 로 펼친 뒤 조각(간격 ≥ 18px) 단위 교체.
translation/img/tuto.json {key: {"roll": R, "tr": {"행.조각": "번역"}}}"""
import sys, os, json
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, lines
KEYS = ['2753', '2754', '2755', '2756', '2757', '2758', '2759']
ST = dict(font='EB', size=23, fill=[222, 222, 222], strokes=[[2, [70, 70, 70]]], align='l', squeeze=0.55)

def find_roll(a):
    """행 시작 글자가 모인 오른쪽 열: 대부분 행에서 잉크가 시작되는 x."""
    m = a[..., 3] > 60
    cols = m.mean(0)
    # 오른쪽 20~60px 에서 비어 있는 열 → 그 다음이 시작
    for x in range(a.shape[1] - 1, a.shape[1] - 90, -1):
        if cols[x] < 0.01: return a.shape[1] - (x + 1)
    return 0

ROLL = {'2759': 24, '2758': 36}

def segs(a, gap=8, pitch=None):
    m = a[..., 3] > 60
    rows = []
    for y0, y1 in [t for t in lines.runs(m.any(1)) if t[1] - t[0] >= 6]:
        n = max(1, round((y1 - y0) / 24.5)) if y1 - y0 > 40 else 1
        for j in range(n): rows.append((y0 + (y1 - y0) * j // n, y0 + (y1 - y0) * (j + 1) // n))
    out = []
    for y0, y1 in rows:
        rr = []
        for s, e in lines.runs(m[y0:y1].any(0)):
            if rr and s - rr[-1][1] < gap: rr[-1] = (rr[-1][0], e)
            else: rr.append((s, e))
        out.append([(y0, y1, s, e) for s, e in rr])
    return out

def sheet():
    f = ImageFont.truetype(os.path.join(grp.ROOT, 'NanumSquareNeo-cBd.ttf'), 13)
    for k in KEYS:
        d, i, a = grp.load(k); R = ROLL.get(k, find_roll(a)); a = np.roll(a, R, 1)
        im = Image.fromarray(a.astype(np.uint8)); bg = Image.new('RGBA', im.size, (40, 40, 60, 255)); bg.alpha_composite(im); bg = bg.convert('RGB')
        bg = bg.resize((bg.width * 2, bg.height * 2)); dr = ImageDraw.Draw(bg)
        for r, row in enumerate(segs(a)):
            for c, (y0, y1, s, e) in enumerate(row):
                dr.rectangle([s * 2, y0 * 2, e * 2, y1 * 2], outline=(255, 0, 0)); dr.text((s * 2 + 2, y0 * 2 - 12), '%d.%d' % (r, c), fill=(255, 255, 0), font=f)
        bg.save(os.path.join(grp.ROOT, 'work', 'tuto_%s.png' % k)); print(k, R, len(segs(a)))

def auto_icons(a, y0, y1):
    sub = a[y0:y1]; m = ((sub[..., 3] > 100) & (sub[..., :3].mean(-1) < 200)).astype(np.uint8)
    o = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8))
    return [[s_, e_] for s_, e_ in lines.runs(o.sum(0) > 0) if e_ - s_ >= 8]

def run():
    spec = json.load(open(os.path.join(grp.TR, 'tuto.json'), encoding='utf-8'))
    outs = []
    for k, sp in spec.items():
        d, i, a = grp.load(k); R = ROLL.get(k, find_roll(a)); a = np.roll(a, R, 1); b = a.copy()
        S = segs(a)
        rows = [(row[0][0], row[0][1]) for row in S]
        for (y0, y1) in rows: b[max(0, y0 - 1):y1 + 1, :, 3] = 0
        f = render.font(ST['font'], ST['size'])
        for rk, items in sp['rows'].items():
            y0, y1 = rows[int(rk)]
            icons = sp.get('icons', {}).get(rk) or auto_icons(a, y0, y1)
            for x0, x1, t in items:
                ink = np.nonzero((a[y0:y1, x0:x1, 3] > 60).any(0))[0]
                if len(ink): x1 = x0 + int(ink.max()) + 1   # 게임은 원문 폭만큼만 잘라 표시
                ic = [c for c in icons if c[0] >= x0 - 3 and c[1] <= x1 + 3]
                parts = t.split('@'); assert len(parts) - 1 <= len(ic), (k, rk, t, ic)
                tw = [f.getlength(p) + 2 for p in parts]
                iw = [c[1] - c[0] for c in ic[:len(parts) - 1]]
                total = sum(tw) + sum(iw) + 2 * len(iw)
                sq = min(1.0, (x1 - x0) / total)
                x = x0
                for j, p in enumerate(parts):
                    w = int(np.ceil(tw[j] * sq))
                    if p.strip(): render.draw(b, p, (x, y0, x + w + 2, y1), dict(ST, squeeze=0.4))
                    x += w
                    if j < len(iw):
                        c = ic[j]; x += 1
                        b[y0:y1, x:x + iw[j]] = a[y0:y1, c[0]:c[1]]
                        x += iw[j] + 1
        nd = grp.write(k, d, np.roll(b, -R, 1))
        pv = os.path.join(grp.PREVIEW, k + '.png')
        im = Image.fromarray(np.roll(grp.imgedit.load(nd)[1], R, 1).astype(np.uint8)); bg = Image.new('RGBA', im.size, (40, 40, 60, 255)); bg.alpha_composite(im); bg.convert('RGB').save(pv)
        outs.append(pv)
    grp.contact(outs, os.path.join(grp.ROOT, 'work', 'pv_tuto.png'), cols=2)

if __name__ == '__main__':
    sheet() if sys.argv[1:] == ['sheet'] else run()
