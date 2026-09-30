"""POM 텍스처: 0x40 헤더 [POM][w][h][flags][0][0][clut: 색수|(추가팔레트수<<16)][크기][TEX0 lo][TEX0 hi]...
그 뒤 팔레트(1번째) + (추가 팔레트마다 16B 머리 + 팔레트), 이어서 픽셀(선형), 끝에 선택적 16B 이름."""
import struct
import numpy as np
BPP = {0x13: 8, 0x14: 4, 0x1b: 8, 0x24: 4, 0x2c: 4, 0: 32, 2: 16}
def info(d):
    h = struct.unpack_from('<16I', d, 0)
    hh, w = h[1], h[2]; psm = (h[8] >> 20) & 0x3f; bpp = BPP[psm]
    ncol = h[6] & 0xffff; ncl = (h[6] >> 16) + 1; mode = (h[3] >> 16) & 0xff
    csz = ncol * 4; pixlen = w * hh * bpp // 8
    if mode == 0:
        clut = 0x40; pix = 0x40 + ncl * csz + (ncl - 1) * 16
    else:  # 미리 만든 DMA 패킷 포함: 픽셀은 끝(16B 이름 앞), 팔레트는 패킷 사이
        pix = len(d) - 16 - pixlen
        clut = 0xb0 if mode == 1 else 0xc0
    return dict(w=w, h=hh, psm=psm, bpp=bpp, ncol=ncol, ncl=ncl, clut=clut, pix=pix,
                pixlen=pixlen, mode=mode)
def clut_off(i, n):
    return i['clut'] + n * (i['ncol'] * 4 + 16)
def unswz(pal):
    if len(pal) == 256:
        idx = np.arange(256); idx = (idx & ~0x18) | ((idx & 8) << 1) | ((idx & 16) >> 1)
        return pal[idx]
    return pal
def swz(pal):
    return unswz(pal)  # 자기 역
def palette(d, i, n=0):
    o = clut_off(i, n)
    p = np.frombuffer(d, np.uint8, i['ncol'] * 4, o).reshape(-1, 4)
    return unswz(p)
def indices(d, i):
    raw = np.frombuffer(d, np.uint8, i['pixlen'], i['pix'])
    if i['bpp'] == 8: return raw.reshape(i['h'], i['w'])
    if i['bpp'] == 4:
        out = np.empty(raw.size * 2, np.uint8); out[0::2] = raw & 15; out[1::2] = raw >> 4
        return out.reshape(i['h'], i['w'])
    raise ValueError('bpp')
def rgba(d, n=0):
    i = info(d)
    if i['bpp'] == 32:
        a = np.frombuffer(d, np.uint8, i['w'] * i['h'] * 4, i['clut']).reshape(i['h'], i['w'], 4).copy()
    else:
        a = palette(d, i, n)[indices(d, i)].copy()
    a[..., 3] = np.minimum(255, a[..., 3].astype(int) * 2)
    return a
def set_indices(d, i, idx):
    d = bytearray(d); idx = idx.astype(np.uint8).reshape(-1)
    if i['bpp'] == 8: raw = idx
    else: raw = (idx[0::2] & 15) | ((idx[1::2] & 15) << 4)
    d[i['pix']:i['pix'] + i['pixlen']] = raw.tobytes(); return bytes(d)
def set_palette(d, i, pal, n=0):
    d = bytearray(d); o = clut_off(i, n)
    d[o:o + i['ncol'] * 4] = swz(np.asarray(pal, np.uint8)).tobytes(); return bytes(d)
