"""캐릭터 프로필 v_* (항목 2765~2801)."""
import sys, os, json
import numpy as np, cv2
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render
KEYS = [str(k) for k in range(2765, 2802)]
SILVER = {'v': [[252, 252, 251], [196, 197, 198]]}
NAME = dict(font='H', size=28, italic=0.1, fill=SILVER, strokes=[[3, [0, 22, 80]]], align='l', squeeze=0.7)
KIND = dict(font='EB', size=19, fill=SILVER, strokes=[[3, [0, 22, 80]]], align='l', squeeze=0.8)
DATA = dict(font='B', size=18, fill=[250, 76, 126], strokes=[[2, [40, 10, 40]]], align='l', squeeze=0.7)
DESC = dict(font='B', size=16, fill=[250, 250, 249], glow=[1, [3, 133, 217], 1.2, 1.0], align='l', valign='t', lead=21, squeeze=0.66)

def textmask(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = ((r > 150) & (g > 150)) | ((r > 170) & (g < 150))
    out = np.zeros_like(m)
    out[8:40, 28:462] = m[8:40, 28:462]
    out[49:72, 28:462] = m[49:72, 28:462]
    out[80:168, 29:444] = m[80:168, 29:444]
    return out

def prep():
    L = {k: grp.load(k) for k in KEYS}
    A = np.stack([L[k][2] for k in KEYS])
    M = np.stack([cv2.dilate(textmask(a).astype(np.uint8), np.ones((7, 7), np.uint8)).astype(bool) for a in A])
    for m in M:
        m[:, :27] = False; m[:, 463:] = False; m[:6] = False; m[170:] = False
        m[73:79, :] = False; m[:, 444:447] &= False
    S = np.where(M[..., None], np.nan, A)
    import warnings; warnings.simplefilter('ignore')
    bg = np.nanmedian(S, 0)
    hole = np.isnan(bg[..., 0])
    bg = np.where(np.isnan(bg), 0, bg).astype(np.float32)
    if hole.any():
        u8 = bg.astype(np.uint8)
        bg[..., :3] = cv2.inpaint(np.ascontiguousarray(u8[..., :3]), hole.astype(np.uint8), 4, cv2.INPAINT_TELEA)
        bg[..., 3] = 255
    return L, M, bg, hole

def run():
    tr = json.load(open(os.path.join(grp.TR, 'profile.json'), encoding='utf-8'))
    L, M, bg, hole = prep()
    from PIL import Image
    Image.fromarray(bg.astype(np.uint8)).save(os.path.join(grp.ROOT, 'work', 'bg_profile.png'))
    outs = []
    for j, k in enumerate(KEYS):
        d, i, a = L[k]; t = tr[k]
        b = a.copy(); b[M[j]] = bg[M[j]]
        x = 36
        if 'kind' in t:
            render.draw(b, t['kind'], (36, 12, 200, 35), dict(KIND, valign='b'))
            f = render.font('EB', 19)
            x = 36 + int(f.getlength(t['kind'])) + 16
        render.draw(b, t['name'], (x, 10, 440, 36), dict(NAME, valign='b'))
        render.draw(b, '- DATA -  신장  %s  - 체중  %s -' % (t['h'], t['w']), (31, 53, 440, 69), DATA)
        render.draw(b, t['d'], (34, 86, 440, 166), DESC)
        nd = grp.write(k, d, b)
        grp.preview(k, nd, crop=(0, 0, 470, 180))
        outs.append(os.path.join(grp.PREVIEW, k + '.png'))
    for j in range(0, len(outs), 8):
        grp.contact(outs[j:j + 8], os.path.join(grp.ROOT, 'work', 'pv_pf%d.png' % (j // 8)), cols=2)

if __name__ == '__main__':
    run()
