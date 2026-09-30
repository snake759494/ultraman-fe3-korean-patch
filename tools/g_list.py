"""목록형 글자 그림(투명 배경, 줄마다 한 항목) 공통 처리.
translation/img/lists.json:
  { "<key>": {"style": "<양식이름>", "slots": [[x0,y0,x1,y1,"번역"], ...] 또는
              "pitch": 46, "first": 0, "h": 45, "items": ["번역", ...], "grow": 1.15, "also": ["fum:..."] } }
- 각 칸은 투명하게 지운 뒤 번역을 그린다. 폭은 원래 잉크 폭 × grow 까지(넘치면 압축).
"""
import sys, os, json
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
import gimg as grp, render, assets

SILVER = {'v': [[255, 255, 255], [168, 170, 176]]}
STYLES = {
    # 캐릭터 선택 이름: 굵은 기울임, 은색, 짙은 회색 외곽
    'selname': dict(font='H', size=36, italic=0.18, fill=SILVER, strokes=[[3, [30, 30, 36]]], align='l', squeeze=0.55),
    # 작은 흰 목록 글자
    'white_s': dict(font='EB', size=13, fill=[235, 235, 235], align='l', squeeze=0.6),
    'white_m': dict(font='EB', size=16, fill=[240, 240, 240], strokes=[[1, [20, 20, 20]]], align='l', squeeze=0.6),
}

def ink_box(a, box):
    x0, y0, x1, y1 = box
    m = a[y0:y1, x0:x1, 3] > 40
    if not m.any(): return None
    ys, xs = np.nonzero(m)
    return x0 + xs.min(), y0 + ys.min(), x0 + xs.max() + 1, y0 + ys.max() + 1

def run(only=None):
    spec = json.load(open(os.path.join(grp.TR, 'lists.json'), encoding='utf-8'))
    outs = []
    for k, s in spec.items():
        if only and k not in only: continue
        d, i, a = grp.load(k)
        st = dict(STYLES[s['style']], **s.get('st', {}))
        b = a.copy()
        slots = s.get('slots')
        if not slots:
            P, f0, h = s['pitch'], s.get('first', 0), s['h']
            slots = []
            for n, t in enumerate(s['items']):
                y0 = f0 + n * P
                ib = ink_box(a, (0, y0, a.shape[1], min(a.shape[0], y0 + h)))
                x1 = int(ib[2] * s.get('grow', 1.15)) if ib else a.shape[1]
                if s.get('uvw'): x1 = s.get('maxw', 216)
                slots.append([0, y0, min(a.shape[1] - 1, max(x1, s.get('minw', 0))), min(a.shape[0], y0 + h), t])
        for x0, y0, x1, y1, t in slots:
            b[y0:y1, :, 3] = 0 if s.get('fullrow', 1) else b[y0:y1, :, 3]
            if not s.get('fullrow', 1): b[y0:y1, x0:x1, 3] = 0
            if t: render.draw(b, t, (x0 + s.get('pad', 1), y0, x1, y1), st)
        nd = grp.write(k, d, b)
        if s.get('uvw'):  # 실제 잉크 폭을 기록 → build.py 가 실행파일 UV 표의 폭을 고침
            i2, a2 = grp.imgedit.load(nd)
            ws = {}
            for x0, y0, x1, y1, t in slots:
                ib = ink_box(a2, (0, y0, a2.shape[1], y1))
                if ib: ws[int(y0)] = int(min(a2.shape[1], ib[2] + 2))
            json.dump(ws, open(os.path.join(grp.PATCHED, 'uvw_%s.json' % s['uvw']), 'w'))
        for extra in s.get('also', []):
            assert assets.get(extra) == assets.get(k), extra
            open(os.path.join(grp.PATCHED, assets.safe(extra) + '.pom'), 'wb').write(nd)
        grp.preview(k, nd)
        outs.append(os.path.join(grp.PREVIEW, assets.safe(k) + '.png'))
    return outs

if __name__ == '__main__':
    outs = run(sys.argv[1:] or None)
    grp.contact(outs, os.path.join(grp.ROOT, 'work', 'pv_list.png'), cols=min(6, len(outs)))
