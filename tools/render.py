"""한글 글자 렌더링 (RGBA float 캔버스 위에 합성, 알파는 표시값 0~255).
양식(style) 키:
  font: 'L','R','B','EB','H' (NanumSquareNeo 굵기) / 'SH-L','SH-M','SH-B','SH-EB' (서울한강)
  size: 글꼴 크기(px). 넘치면 squeeze(기본 0.75)까지 가로 압축, 그래도 넘치면 크기 축소
  fill: [r,g,b] | {'v':[위,아래]} | {'h':[왼,오른]}  (그라데이션은 줄마다 잉크 범위 기준)
  strokes: [[폭,[r,g,b]], ...]  바깥→안쪽 순 (폭이 큰 것부터)
  glow: [폭,[r,g,b],흐림,세기]   shadow: [dx,dy,[r,g,b,a]]
  italic: 기울기(0.2 ≈ 11도)   track: 자간   lead: 줄 간격   cap: 한글 잉크 높이(기본 size*0.8)
  align: l/c/r   valign: t/m/b   dx, dy: 미세 이동"""
import os
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FONTS = {'L': 'NanumSquareNeo-aLt.ttf', 'R': 'NanumSquareNeo-bRg.ttf', 'B': 'NanumSquareNeo-cBd.ttf',
         'EB': 'NanumSquareNeo-dEb.ttf', 'H': 'NanumSquareNeo-eHv.ttf',
         'SH-L': 'SeoulHangangL.ttf', 'SH-M': 'SeoulHangangM.ttf', 'SH-B': 'SeoulHangangB.ttf', 'SH-EB': 'SeoulHangangEB.ttf'}
_fc = {}
def font(name, size):
    k = (name, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(os.path.join(ROOT, FONTS[name]), size)
    return _fc[k]

PAD = 12

def _render_line(text, f, track, widths):
    """한 줄: {0: 몸통, w: 폭 w 외곽 포함 마스크}. 기준 원점 (PAD, PAD) 에 글꼴 top."""
    ws = [f.getlength(ch) for ch in text]
    W = int(np.ceil(sum(ws) + track * max(0, len(text) - 1))) + 2 * PAD
    asc, desc = f.getmetrics(); H = asc + desc + 2 * PAD
    out = {}
    for w in [0] + sorted(set(widths)):
        im = Image.new('L', (W, H)); d = ImageDraw.Draw(im); x = PAD
        for ch, cw in zip(text, ws):
            if w: d.text((x, PAD), ch, font=f, fill=255, stroke_width=w, stroke_fill=255)
            else: d.text((x, PAD), ch, font=f, fill=255)
            x += cw + track
        out[w] = np.asarray(im, np.float32) / 255
    return out

def _ink(m, thr=0.05):
    ys, xs = np.nonzero(m > thr)
    if len(xs) == 0: return 0, 0, 1, 1
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1

def _xform(m, sx, italic):
    """가로 압축 sx, 기울임(위쪽이 오른쪽으로)."""
    h, w = m.shape
    nw = int(np.ceil(w * sx + abs(italic) * h)) + 2
    # x' = sx*x + italic*(h - y)
    M = np.float32([[sx, -italic, italic * h], [0, 1, 0]])
    return cv2.warpAffine(m, M, (nw, h), flags=cv2.INTER_AREA if sx < 1 else cv2.INTER_LINEAR)

def layout(text, box, st):
    lines = text.split('\n')
    x0, y0, x1, y1 = box; bw, bh = x1 - x0, y1 - y0
    size = st['size']; widths = [w for w, c in st.get('strokes', [])]
    maxw = max(widths) if widths else 0
    minsq = st.get('squeeze', 0.75); it = st.get('italic', 0)
    while True:
        f = font(st.get('font', 'B'), size)
        rl = [_render_line(t, f, st.get('track', 0), widths) for t in lines]
        cap = st.get('cap', size * 0.8) * size / st['size']
        lead = st.get('lead', size * 1.3) * size / st['size']
        inkw = []
        for r in rl:
            a, b, c, d = _ink(r[maxw]); inkw.append(c - a + it * cap)
        need = max(inkw) if inkw else 1
        sq = min(1.0, bw / need)
        if st.get('justify') and len(lines) == 1 and need < bw and len(lines[0]) > 1 and not st.get('_j'):
            st = dict(st, track=st.get('track', 0) + (bw - need) / (len(lines[0]) - 1), _j=1)
            continue
        toth = lead * (len(lines) - 1) + cap + 2 * maxw
        if (sq >= minsq and toth <= bh + 1) or size <= 7:
            break
        size -= 1
    asc = f.getmetrics()[0]
    # 한글 글꼴 잉크 top 위치(글꼴 top 기준) 를 '가' 로 측정
    probe = _render_line('가', f, 0, [])[0]; _, pt, _, pb = _ink(probe); ink_top = pt; ink_h = pb - pt
    blk = lead * (len(lines) - 1) + ink_h
    va = st.get('valign', 'm')
    top = y0 + (0 if va == 't' else (bh - blk) / 2 if va == 'm' else bh - blk) + st.get('dy', 0)
    placed = []
    for li, r in enumerate(rl):
        ms = {w: _xform(m, sq, it) for w, m in r.items()}
        a, b, c, d = _ink(ms[maxw]); wline = c - a
        al = st.get('align', 'c')
        lx = x0 + (0 if al == 'l' else (bw - wline) / 2 if al == 'c' else bw - wline) - a + st.get('dx', 0)
        ly = top + li * lead - ink_top
        placed.append((ms, int(round(lx)), int(round(ly))))
    return placed, size, sq

def _paste(dst, m, x, y):
    H, W = dst.shape; h, w = m.shape
    sx0, sy0 = max(0, -x), max(0, -y); dx0, dy0 = max(0, x), max(0, y)
    ww = min(w - sx0, W - dx0); hh = min(h - sy0, H - dy0)
    if ww > 0 and hh > 0:
        np.maximum(dst[dy0:dy0 + hh, dx0:dx0 + ww], m[sy0:sy0 + hh, sx0:sx0 + ww], out=dst[dy0:dy0 + hh, dx0:dx0 + ww])

def over(dst, color, alpha):
    """dst 위에 color(rgb 또는 H×W×3) 를 alpha(H×W, 0~1) 로 합성."""
    a = np.clip(alpha, 0, 1)[..., None]
    col = np.asarray(color, np.float32)[..., :3]
    da = dst[..., 3:4] / 255
    oa = a + da * (1 - a)
    rgb = (col * a + dst[..., :3] * da * (1 - a)) / np.maximum(oa, 1e-6)
    dst[..., :3] = np.where(oa > 0, rgb, dst[..., :3]); dst[..., 3:4] = oa * 255
    return dst

def masks(canvas_shape, text, box, st):
    placed, size, sq = layout(text, box, st)
    H, W = canvas_shape[:2]
    keys = placed[0][0].keys() if placed else [0]
    out = {k: np.zeros((H, W), np.float32) for k in keys}
    for ms, x, y in placed:
        for k, m in ms.items(): _paste(out[k], m, x, y)
    return out, placed, size, sq

def draw(canvas, text, box, st):
    """canvas(H×W×4 float) 의 box 안에 text 를 그린다. 반환 (크기, 압축비)."""
    H, W = canvas.shape[:2]
    ms, placed, size, sq = masks(canvas.shape, text, box, st)
    widths = sorted([w for w, c in st.get('strokes', [])], reverse=True)
    outer = ms[widths[0]] if widths else ms[0]
    if 'shadow' in st:
        dx, dy, c = st['shadow']
        sh = np.zeros_like(outer)
        sh[max(0, dy):H + min(0, dy), max(0, dx):W + min(0, dx)] = outer[max(0, -dy):H - max(0, dy), max(0, -dx):W - max(0, dx)]
        over(canvas, c[:3], sh * (c[3] / 255 if len(c) > 3 else 1))
    if 'glow' in st:
        gw, gc, blur, k = st['glow']
        g = cv2.dilate(outer, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * gw + 1, 2 * gw + 1)))
        if blur: g = cv2.GaussianBlur(g, (0, 0), blur)
        over(canvas, gc, np.minimum(1, g * k))
    def colorize(fill):
        if not isinstance(fill, dict): return fill
        col = np.zeros((H, W, 3), np.float32)
        (kind, (c0, c1)), = fill.items()
        c0 = np.asarray(c0, np.float32); c1 = np.asarray(c1, np.float32)
        for m, x, y in placed:
            ref = m[max(m.keys())]
            a_, b_, c_, d_ = _ink(ref)
            if kind == 'v':
                r0, r1 = max(0, y), min(H, y + ref.shape[0])
                t = np.clip((np.arange(r0, r1) - (y + b_)) / max(1, d_ - b_ - 1), 0, 1)[:, None, None]
                col[r0:r1, max(0, x):min(W, x + ref.shape[1])] = c0 * (1 - t) + c1 * t
            else:
                q0, q1 = max(0, x), min(W, x + ref.shape[1])
                t = np.clip((np.arange(q0, q1) - (x + a_)) / max(1, c_ - a_ - 1), 0, 1)[None, :, None]
                col[max(0, y):min(H, y + ref.shape[0]), q0:q1] = c0 * (1 - t) + c1 * t
        return col
    for w, c in sorted(st.get('strokes', []), key=lambda x: -x[0]):
        over(canvas, colorize(c), ms[w])
    fill = st.get('fill', [255, 255, 255])
    body = ms[0]
    if fill == 'none':
        canvas[..., 3] *= (1 - np.clip(body * 1.3, 0, 1))
    else:
        over(canvas, colorize(fill), body)
    return size, sq

def roll_x(a, s):
    return np.roll(a, s, 1)
