"""POM 그림 편집: RGBA(표시 알파 0~255) 로 읽고, 원래 팔레트로 양자화해 되돌린다."""
import numpy as np
from scipy.spatial import cKDTree
import pom

def load(d, n=0):
    """(정보, RGBA float32 H×W×4). 알파는 표시값(0x80→255)."""
    i = pom.info(d)
    return i, pom.rgba(d, n).astype(np.float32)

def pal_disp(d, i, n=0):
    p = pom.palette(d, i, n).astype(np.float32).copy()
    p[:, 3] = np.minimum(255, p[:, 3] * 2)
    return p

def _feat(c):
    a = c[..., 3:4] / 255.0
    return np.concatenate([c[..., :3] * a, c[..., 3:4] * 1.2], -1)

def quantize(d, rgba, mask=None, n=0, regions=None):
    """rgba 를 팔레트 번호로. mask(bool H×W) 가 주어지면 그 부분만 다시 고르고 나머지는 원래 번호 유지."""
    i = pom.info(d)
    pal = pal_disp(d, i, n)
    tree = cKDTree(_feat(pal))
    idx = pom.indices(d, i).copy()
    sel = np.ones(idx.shape, bool) if mask is None else mask
    orig = idx.copy()
    q = rgba[sel]
    _, k = tree.query(_feat(q))
    idx[sel] = k
    # 다중 팔레트: 영역마다 원래 쓰인 번호로만 제한
    for (x0, y0, x1, y1) in (regions or []):
        allowed = np.unique(orig[y0:y1, x0:x1])
        sub = rgba[y0:y1, x0:x1]
        t = cKDTree(_feat(pal[allowed]))
        _, kk = t.query(_feat(sub.reshape(-1, 4)))
        idx[y0:y1, x0:x1] = allowed[kk].reshape(sub.shape[:2])
    return idx

def save(d, rgba, mask=None, n=0, regions=None):
    i = pom.info(d)
    idx = quantize(d, rgba, mask, n, regions)
    return pom.set_indices(d, i, idx)

def changed_mask(orig, new, tol=1.0):
    return np.abs(orig - new).max(-1) > tol
