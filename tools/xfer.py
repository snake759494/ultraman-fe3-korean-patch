"""번호 전이: 원본 글자 영역의 팔레트 번호를 (외곽까지 거리, 상대 세로 위치) 기준으로 새 글자에 옮긴다.
팔레트를 건드리지 않으므로 다중 팔레트·특수 효과 글자에도 쓸 수 있다.
spec: translation/img/xfer.json {key: {"roll": 0, "items": [[x0,y0,x1,y1,"번역",{font,size,italic,stroke,align}]], "also": []}}"""
import sys, os, json
import numpy as np, cv2
from scipy.spatial import cKDTree
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, pom, assets

def transparent_index(d, i):
    p = pom.palette(d, i)
    return int(np.argmin(p[:, 3]))

def depth(mask):
    return cv2.distanceTransform(mask.astype(np.uint8), cv2.DIST_L2, 3)

def xfer_region(idx, tidx, box, text, st):
    x0, y0, x1, y1 = box
    sub = idx[y0:y1, x0:x1]
    ink = sub != tidx
    if not ink.any(): return idx
    ys, xs = np.nonzero(ink)
    oy0, oy1 = ys.min(), ys.max() + 1
    dep = depth(np.pad(ink, 1))[1:-1, 1:-1]
    ox0, ox1 = xs.min(), xs.max() + 1
    axis = st.get('axis', 'y')
    rel = (ys - oy0) / max(1, oy1 - oy0) if axis == 'y' else (xs - ox0) / max(1, ox1 - ox0)
    feat = np.stack([np.minimum(dep[ink], st.get('dmax', 99)) * 1.0, rel * st.get('yw', 6.0)], 1)
    vals = sub[ink]
    tree = cKDTree(feat)
    # 새 글자 마스크
    H, W = sub.shape
    can = np.zeros((H, W, 4), np.float32)
    sw = st.get('stroke', 3)
    rs = dict(font=st.get('font', 'H'), size=st.get('size', int((oy1 - oy0) * 1.12)), italic=st.get('italic', 0), align=st.get('align', 'c'), valign=st.get('valign', 'm'),
              squeeze=st.get('squeeze', 0.6), fill=[255, 255, 255], strokes=[[sw, [255, 255, 255]]] if sw else [])
    render.draw(can, text, (st.get('pad', 1), int(oy0), W - st.get('pad', 1), int(oy1)), rs)
    nm = can[..., 3] > 110
    out = sub.copy(); out[:] = tidx
    if nm.any():
        ny, nx = np.nonzero(nm)
        nd = depth(np.pad(nm, 1))[1:-1, 1:-1]
        ny0, ny1 = ny.min(), ny.max() + 1; nx0, nx1 = nx.min(), nx.max() + 1
        nrel = (ny - ny0) / max(1, ny1 - ny0) if axis == 'y' else (nx - nx0) / max(1, nx1 - nx0)
        q = np.stack([np.minimum(nd[nm], st.get('dmax', 99)), nrel * st.get('yw', 6.0)], 1)
        _, k = tree.query(q)
        out[nm] = vals[k]
        # 다수결 3×3 (잡점 제거)
        cand = np.unique(out[nm])
        cnt = np.stack([cv2.blur((out == c).astype(np.float32), (3, 3)) for c in cand])
        maj = cand[np.argmax(cnt, 0)]
        out[nm] = maj[nm]
    idx[y0:y1, x0:x1] = out
    return idx

def run(only=None):
    spec = json.load(open(os.path.join(grp.TR, 'xfer.json'), encoding='utf-8'))
    outs = []
    for k, s in spec.items():
        if k.startswith('_') or (only and k not in only): continue
        d = assets.get(k); i = pom.info(d)
        idx = np.roll(pom.indices(d, i).copy(), s.get('roll', 0), 1)
        t = s.get('tidx', transparent_index(d, i))
        for it in s['items']:
            x0, y0, x1, y1, text = it[:5]; st = it[5] if len(it) > 5 else {}
            idx = xfer_region(idx, t, (x0, y0, x1, y1), text, dict(s.get('st', {}), **st))
        nd = pom.set_indices(d, i, np.roll(idx, -s.get('roll', 0), 1))
        open(os.path.join(grp.PATCHED, assets.safe(k) + '.pom'), 'wb').write(nd)
        for e in s.get('also', []): open(os.path.join(grp.PATCHED, assets.safe(e) + '.pom'), 'wb').write(nd)
        # 미리보기: 각 팔레트로
        from PIL import Image
        ims = []
        for n in range(i['ncl'] if i['bpp'] < 32 else 1):
            a = np.roll(pom.rgba(nd, n), s.get('roll', 0), 1)
            im = Image.fromarray(a); bg = Image.new('RGBA', im.size, (60, 30, 70, 255)); bg.alpha_composite(im)
            if 'view' in s: bg = bg.crop(tuple(s['view']))
            ims.append(bg.convert('RGB'))
        W = max(x.width for x in ims); H = sum(x.height for x in ims)
        c = Image.new('RGB', (W, H)); y = 0
        for x in ims: c.paste(x, (0, y)); y += x.height
        p = os.path.join(grp.PREVIEW, assets.safe(k) + '.png'); c.save(p); outs.append(p)
    return outs

if __name__ == '__main__':
    o = run(sys.argv[1:] or None)
    grp.contact(o, os.path.join(grp.ROOT, 'work', 'pv_xfer.png'), cols=2)
