"""한글판 ISO 빌드: 원본 ISO 복사 → work/patched/*.pom 반영 → 색인·ISO 레코드 갱신.
단독 POM 은 같은 크기로 제자리, FUM 멤버는 DFS 재압축 후 FUM 재구성(넘치면 ISO 끝에 추가)."""
import os, sys, struct, shutil, time
sys.path.insert(0, os.path.dirname(__file__))
import ftab, fum, dfs, assets, isopatch
ROOT = ftab.ROOT
SRC = ftab.ISO
DST = os.path.join(ROOT, 'Ultraman - Fighting Evolution 3 (Japan) (Korean).iso')
PATCHED = os.path.join(ROOT, 'work', 'patched')
ELF_LBA = 356
SEC = 2048

def load_patches():
    out = {}
    for fn in sorted(os.listdir(PATCHED)):
        if not fn.endswith('.pom'): continue
        k = fn[:-4]
        key = 'fum:' + k[2:].replace('~', '/') if k.startswith('F_') else k
        out[key] = open(os.path.join(PATCHED, fn), 'rb').read()
    return out

def rebuild_fum(d, repl):
    ms = fum.parse(d); n = len(ms)
    hdr = bytearray(d[:8 + 0x80 * n])
    pos = (8 + 0x80 * n + 0x3f) & ~0x3f
    body = bytearray(pos)
    for k, (name, o, a, s) in enumerate(ms):
        m = d[o:o + s]
        if name in repl: m = repl[name]
        al = (len(m) + 0x3f) & ~0x3f
        struct.pack_into('<3I', hdr, 8 + 0x80 * k + 0x74, pos, al, len(m))
        body += m + bytes(al - len(m)); pos += al
    body[:len(hdr)] = hdr
    return bytes(body)

# 캐릭터 선택 이름 UV 표 (x, y, 폭, 46, 모드, 0) × [이름판1 22칸 + 이름판2 18칸] 반복
SELNAME_TABLES = [0x1c9180, 0x1c9390, 0x1d04d8, 0x1d06e8, 0x1d7ad8]

def elf_uv(elf):
    import json
    p1 = os.path.join(PATCHED, 'uvw_selname1.json'); p2 = os.path.join(PATCHED, 'uvw_selname2.json')
    if not (os.path.exists(p1) and os.path.exists(p2)): return
    w1 = {int(k): v for k, v in json.load(open(p1)).items()}; w2 = {int(k): v for k, v in json.load(open(p2)).items()}
    n = 0
    for base in SELNAME_TABLES:
        r = 0; tex = 1; prev = -1
        while True:
            x, y, w, h, m, z = struct.unpack_from('<6i', elf, base + 24 * r)
            if h != 46: break
            if y <= prev: tex = 2 if tex == 1 else 1
            prev = y
            nw = (w1 if tex == 1 else w2).get(y)
            if nw: struct.pack_into('<i', elf, base + 24 * r + 8, nw); n += 1
            r += 1
    print('이름 UV 폭 수정', n)

def main(dst=DST):
    t0 = time.time()
    patches = load_patches()
    elf = bytearray(ftab.elf_orig())
    tab = ftab.table(elf)
    stand = {int(k): v for k, v in patches.items() if not k.startswith('fum:')}
    fumrep = {}
    for k, v in patches.items():
        if k.startswith('fum:'):
            orig = assets.get(k)
            if v == orig: continue
            # 원래 DFS 였는지
            i, j = assets.fum_index()[k[4:]][0]
            m = fum.members(assets.entry(i))[j][1]
            fumrep[k[4:]] = dfs.compress(v) if m[:4] == b'DFS\x01' else v
    touched = {}
    for name in fumrep:
        for i, j in assets.fum_index()[name]:
            touched.setdefault(i, {})[name] = fumrep[name]
    print('단독', len(stand), 'FUM멤버', len(fumrep), 'FUM항목', len(touched))
    shutil.copyfile(SRC, dst)  # 항상 원본에서 새로
    f3_lba, f3_size = ftab.FILES[2][1], ftab.FILES[2][2]
    end = f3_lba * SEC + f3_size  # FILE3 끝 = ISO 끝
    with open(dst, 'r+b') as f:
        for i, data in stand.items():
            off, alloc, size, fn = tab[i]
            assert len(data) == size, (i, len(data), size)
            f.seek(ftab.FILES[fn][1] * SEC + off); f.write(data)
        for i, repl in sorted(touched.items()):
            off, alloc, size, fn = tab[i]
            nd = rebuild_fum(assets.entry(i), repl)
            nalloc = (len(nd) + SEC - 1) // SEC * SEC
            if nalloc <= alloc:
                f.seek(ftab.FILES[fn][1] * SEC + off); f.write(nd + bytes(alloc - len(nd)))
                tab[i] = [off, alloc, len(nd), fn]
            else:
                f.seek(end); f.write(nd + bytes(nalloc - len(nd)))
                tab[i] = [end - f3_lba * SEC, nalloc, len(nd), 2]
                end += nalloc
        for i in range(ftab.N):
            struct.pack_into('<4I', elf, ftab.TAB + 16 * i, *tab[i])
        elf_uv(elf)
        f.seek(ELF_LBA * SEC); f.write(elf)
        new_f3 = end - f3_lba * SEC
        if new_f3 != f3_size:
            isopatch.relocate(f, 'FILE3.BIN', f3_lba, new_f3, dir_lba=261, dir_secs=1, udf_part=267, udf_fe=range(275, 355))
        total = max(end, os.path.getsize(SRC))  # 원본 뒤쪽 여백 유지
        if total > os.path.getsize(SRC):
            isopatch.set_volume_size(f, total // SEC, udf_part=267)
        f.truncate(total)
    print('완료', dst, '%.1fs' % (time.time() - t0))

if __name__ == '__main__':
    out = DST
    for a in sys.argv[1:]:
        if a.startswith('--out='): out = a[6:]
    main(out)
