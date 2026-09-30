"""사각형 지정 교체: translation/img/boxes.json
{ "<key>": {"items": [[x0,y0,x1,y1,"번역","양식", {덮어쓸 양식}], ...], "also": [...], "view": [x0,y0,x1,y1]} }
각 사각형: 'bg' 방식으로 원문을 지운 뒤 번역을 그림.
  bg=clear(기본, 투명) | inpaint(글자 픽셀만 주변색으로) | col:X(열 X 를 가로 복제) | rgb:[r,g,b,a] | keep(지우지 않음)
python tools/g_boxes.py grid <key> [x0 y0 x1 y1]   → work/grid.png (좌표 격자)"""
import sys, os, json
import numpy as np, cv2
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, assets
SIL = {'v': [[255, 255, 255], [178, 180, 186]]}
STY = {
 'w': dict(font='B', size=16, fill=[245, 245, 245], align='l', squeeze=0.6),
 'wo': dict(font='EB', size=16, fill=[248, 248, 248], strokes=[[2, [10, 10, 20]]], align='l', squeeze=0.6),
 'wh': dict(font='H', size=20, fill=[250, 250, 250], strokes=[[2, [10, 10, 30]]], align='c', squeeze=0.6),
 'title': dict(font='H', size=30, italic=0.15, fill={'v': [[255, 255, 255], [180, 184, 200]]}, strokes=[[3, [20, 20, 60]]], align='l', squeeze=0.6),
 'red': dict(font='H', size=28, italic=0.15, fill={'v': [[255, 240, 120], [255, 60, 30]]}, strokes=[[3, [60, 0, 0]]], align='l', squeeze=0.6),
 'gray': dict(font='B', size=15, fill=[200, 200, 200], align='l', squeeze=0.6),
 'dark': dict(font='B', size=15, fill=[30, 30, 30], align='l', squeeze=0.6),
}
def erase(b, a, box, mode):
    x0, y0, x1, y1 = box
    if mode == 'keep': return
    if mode == 'clear': b[y0:y1, x0:x1, 3] = 0; return
    if mode.startswith('col:'):
        x = int(mode[4:]); b[y0:y1, x0:x1] = a[y0:y1, x:x + 1]; return
    if mode.startswith('rgb:'):
        b[y0:y1, x0:x1] = json.loads(mode[4:]); return
    if mode == 'blue':
        sub = a[y0:y1, x0:x1]
        if sub.size == 0: return
        m = ((sub[..., 2] - sub[..., 0]) > 60) & (sub[..., 3] > 100)
        m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8))
        u8 = np.ascontiguousarray(a[..., :3].astype(np.uint8))
        full = np.zeros(a.shape[:2], np.uint8); full[y0:y1, x0:x1] = m
        b[..., :3] = np.where(full[..., None] > 0, cv2.inpaint(u8, full, 3, cv2.INPAINT_TELEA), b[..., :3]); return
    if mode.startswith('inpaint'):
        sub = a[y0:y1, x0:x1]
        if sub.size == 0: return
        med = np.median(sub.reshape(-1, 4), 0)
        thr = int(mode[8:]) if len(mode) > 8 else 45
        m = np.abs(sub - med).max(-1) > thr
        m = cv2.dilate(m.astype(np.uint8), np.ones((3, 3), np.uint8))
        u8 = np.ascontiguousarray(a[..., :3].astype(np.uint8))
        full = np.zeros(a.shape[:2], np.uint8); full[y0:y1, x0:x1] = m
        b[..., :3] = np.where(full[..., None] > 0, cv2.inpaint(u8, full, 4, cv2.INPAINT_TELEA), b[..., :3])
        b[y0:y1, x0:x1, 3] = np.where(m > 0, med[3], b[y0:y1, x0:x1, 3])

def run(only=None):
    spec = json.load(open(os.path.join(grp.TR, 'boxes.json'), encoding='utf-8'))
    outs = []
    for k, s in spec.items():
        if k.startswith('_') or (only and k not in only): continue
        d, i, a = grp.load(k)
        R = s.get('roll', 0); a = np.roll(a, R, 1)
        b = a.copy()
        for it in s['items']:
            x0, y0, x1, y1, t, sn = it[:6]; ov = it[6] if len(it) > 6 else {}
            erase(b, a, (x0, y0, x1, y1), ov.get('bg', s.get('bg', 'clear')))
        for it in s['items']:
            x0, y0, x1, y1, t, sn = it[:6]; ov = dict(it[6]) if len(it) > 6 else {}
            ov.pop('bg', None); pad = ov.pop('pad', 0)
            if t: render.draw(b, t, (x0 + pad, y0, ov.pop('tx1', x1 - pad), y1), dict(STY[sn], **ov))
        regs = None
        if i['bpp'] < 32 and i['ncl'] > 1:
            W_ = a.shape[1]; regs = []
            for it in s['items']:
                x0, y0, x1, y1 = it[:4]
                xs = [(x - R) % W_ for x in (x0, x1 - 1)]
                if xs[0] <= xs[1]: regs.append((xs[0], y0, xs[1] + 1, y1))
                else: regs += [(xs[0], y0, W_, y1), (0, y0, xs[1] + 1, y1)]
        nd = grp.write(k, d, np.roll(b, -R, 1), regions=regs)
        for e in s.get('also', []): open(os.path.join(grp.PATCHED, assets.safe(e) + '.pom'), 'wb').write(nd)
        im = Image.fromarray(np.roll(grp.imgedit.load(nd)[1], R, 1).astype(np.uint8)); bgi = Image.new('RGBA', im.size, (60, 30, 70, 255)); bgi.alpha_composite(im)
        if 'view' in s: bgi = bgi.crop(tuple(s['view']))
        bgi.convert('RGB').save(os.path.join(grp.PREVIEW, assets.safe(k) + '.png'))
        outs.append(os.path.join(grp.PREVIEW, assets.safe(k) + '.png'))
    return outs

def grid(k, crop=None, scale=2):
    d, i, a = grp.load(k)
    im = Image.fromarray(a.astype(np.uint8)); bg = Image.new('RGBA', im.size, (60, 30, 70, 255)); bg.alpha_composite(im)
    if crop: bg = bg.crop(crop)
    ox, oy = (crop[0], crop[1]) if crop else (0, 0)
    bg = bg.convert('RGB').resize((bg.width * scale, bg.height * scale), Image.NEAREST); dr = ImageDraw.Draw(bg)
    for x in range((ox // 10) * 10, ox + bg.width // scale, 10):
        X = (x - ox) * scale; dr.line([(X, 0), (X, 4 if x % 50 else 10)], fill=(255, 255, 0))
        if x % 50 == 0: dr.text((X + 1, 10), str(x), fill=(255, 255, 0))
    for y in range((oy // 10) * 10, oy + bg.height // scale, 10):
        Y = (y - oy) * scale; dr.line([(0, Y), (4 if y % 50 else 10, Y)], fill=(0, 255, 255))
        if y % 50 == 0: dr.text((10, Y + 1), str(y), fill=(0, 255, 255))
    bg.save(os.path.join(grp.ROOT, 'work', 'grid.png'))

if __name__ == '__main__':
    if sys.argv[1:2] == ['grid']:
        grid(sys.argv[2], tuple(map(int, sys.argv[3:7])) if len(sys.argv) > 6 else None, int(sys.argv[7]) if len(sys.argv) > 7 else 2)
    else:
        o = run(sys.argv[1:] or None)
        grp.contact(o, os.path.join(grp.ROOT, 'work', 'pv_boxes.png'), cols=2)
