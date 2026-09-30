"""글자 그림 묶음 처리 공통 도구.
- 묶음(group) 의 그림들을 읽고, 픽셀 중앙값으로 '글자 없는 배경'을 만든다.
- 글자 마스크 → 줄 상자 검출 → 번호 붙인 확대 시트(번역 작업용)
- 번역 JSON(translation/img/<group>.json): {key: [{"box":[x0,y0,x1,y1], "jp":..., "ko":..., "st":양식이름}, ...]}"""
import os, sys, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, os.path.dirname(__file__))
import assets, imgedit, pom, lines, render
ROOT = assets.ROOT
TR = os.path.join(ROOT, 'translation', 'img')
SHEETS = os.path.join(ROOT, 'work', 'linesheets')
PATCHED = os.path.join(ROOT, 'work', 'patched')
PREVIEW = os.path.join(ROOT, 'work', 'preview')
for d in (TR, SHEETS, PATCHED, PREVIEW): os.makedirs(d, exist_ok=True)

def load(key, n=0):
    d = assets.get(key)
    i, a = imgedit.load(d, n)
    return d, i, a

def median_bg(arrs):
    return np.median(np.stack(arrs), 0).astype(np.float32)

def diff_mask(a, bg, thr=48):
    return np.abs(a - bg).max(-1) > thr

def boxes(mask, gap=2, minh=4, mincol=1):
    return lines.line_boxes(mask, gap=gap, minh=minh)

def sheet(key, img, bxs, out, scale=3, crop=None):
    """번호 붙인 확대 그림."""
    a = img.astype(np.uint8)
    im = Image.fromarray(a, 'RGBA'); bg = Image.new('RGBA', im.size, (40, 40, 60, 255)); bg.alpha_composite(im)
    if crop: bg = bg.crop(crop)
    ox, oy = (crop[0], crop[1]) if crop else (0, 0)
    bg = bg.convert('RGB').resize((bg.width * scale, bg.height * scale), Image.LANCZOS)
    dr = ImageDraw.Draw(bg)
    f = ImageFont.truetype(os.path.join(ROOT, 'NanumSquareNeo-cBd.ttf'), 14)
    for k, (x0, y0, x1, y1) in enumerate(bxs):
        r = [(x0 - ox) * scale - 1, (y0 - oy) * scale - 1, (x1 - ox) * scale, (y1 - oy) * scale]
        dr.rectangle(r, outline=(255, 0, 0))
        dr.text((r[0] - 22 if r[0] > 24 else r[2] + 2, r[1]), str(k), fill=(255, 60, 60), font=f)
    bg.save(out)

def tr_load(group):
    p = os.path.join(TR, group + '.json')
    return json.load(open(p, encoding='utf-8')) if os.path.exists(p) else {}

def tr_save(group, data):
    json.dump(data, open(os.path.join(TR, group + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

def write(key, d, rgba, mask=None, n=0, regions=None):
    nd = imgedit.save(d, rgba, mask, n, regions)
    open(os.path.join(PATCHED, assets.safe(key) + '.pom'), 'wb').write(nd)
    return nd

def preview(key, nd, out=None, n=0, bgcol=(40, 40, 60, 255), crop=None, scale=1):
    i, a = imgedit.load(nd, n)
    im = Image.fromarray(a.astype(np.uint8), 'RGBA'); bg = Image.new('RGBA', im.size, bgcol); bg.alpha_composite(im)
    if crop: bg = bg.crop(crop)
    if scale != 1: bg = bg.resize((bg.width * scale, bg.height * scale), Image.NEAREST)
    bg.convert('RGB').save(out or os.path.join(PREVIEW, assets.safe(key) + '.png'))

def contact(paths, out, cols=2, scale=1.0):
    ims = [Image.open(p) for p in paths]
    w = max(i.width for i in ims); h = max(i.height for i in ims)
    rows = (len(ims) + cols - 1) // cols
    sh = Image.new('RGB', (int(w * cols * scale), int(h * rows * scale)), (90, 90, 90))
    for k, im in enumerate(ims):
        if scale != 1: im = im.resize((int(im.width * scale), int(im.height * scale)), Image.LANCZOS)
        sh.paste(im, (int((k % cols) * w * scale), int((k // cols) * h * scale)))
    sh.save(out)
