"""게임 자산 접근: 단독 항목('2751') 과 FUM 멤버('fum:pom/game_2d/c_man_pom.ENC').
FUM 멤버는 같은 이름이 여러 FUM 에 중복으로 들어 있으므로 이름으로 한꺼번에 다룬다."""
import os, sys, functools
sys.path.insert(0, os.path.dirname(__file__))
import ftab, fum, dfs
ROOT = ftab.ROOT
EXT = os.path.join(ROOT, 'work', 'ext')

@functools.lru_cache(None)
def table():
    return ftab.table(ftab.elf_orig())

def entry(i):
    """항목 원본 바이트(FUM 은 할당크기까지)."""
    p = os.path.join(EXT, '%04d.bin' % i)
    if os.path.exists(p):
        return open(p, 'rb').read()
    t = table()
    return ftab.read_entry(t, i, full=True)

@functools.lru_cache(None)
def fum_index():
    """멤버 이름 → [(항목번호, 멤버순번)]"""
    idx = {}
    t = table()
    for i in range(ftab.N):
        p = os.path.join(EXT, '%04d.bin' % i)
        if not os.path.exists(p): continue
        d = open(p, 'rb').read(8)
        if d[:4] != b'FUM\0': continue
        for k, (n, o, a, s) in enumerate(fum.parse(open(p, 'rb').read())):
            idx.setdefault(n, []).append((i, k))
    return idx

def get(key):
    """자산 원본(압축 해제된) 바이트."""
    if key.startswith('fum:'):
        name = key[4:]
        i, k = fum_index()[name][0]
        m = fum.members(entry(i))[k][1]
        return dfs.decompress(m) if m[:4] == b'DFS\x01' else m
    d = entry(int(key))
    return d[:table()[int(key)][2]]

def safe(key):
    return key.replace('fum:', 'F_').replace('/', '~')
