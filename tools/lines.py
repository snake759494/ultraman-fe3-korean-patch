"""그림에서 글자 줄 영역 찾기 (알파 또는 배경과의 차이 투영)."""
import numpy as np
def runs(v):
    out = []; s = None
    for i, x in enumerate(list(v) + [0]):
        if x and s is None: s = i
        if not x and s is not None: out.append((s, i)); s = None
    return out
def line_boxes(mask, gap=1, minh=3):
    """mask(H×W bool) → [(x0,y0,x1,y1)] 행 단위."""
    rows = mask.any(1); out = []
    rr = runs(rows)
    # 가까운 행 묶음 병합
    merged = []
    for a, b in rr:
        if merged and a - merged[-1][1] <= gap: merged[-1] = (merged[-1][0], b)
        else: merged.append((a, b))
    for a, b in merged:
        if b - a < minh: continue
        cols = np.nonzero(mask[a:b].any(0))[0]
        out.append((int(cols.min()), a, int(cols.max()) + 1, b))
    return out
