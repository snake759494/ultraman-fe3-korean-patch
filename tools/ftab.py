"""SLPS_254.41 안의 FILE1~4.BIN 색인표 (0x214f98, 16B: 오프셋, 할당크기, 실제크기, 파일번호)."""
import struct, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from iso import ISO, ROOT
TAB = 0x214f98; N = 3552
FILES = [('FILE1', 3812, 395907072), ('FILE2', 197126, 512606208),
         ('FILE3', 447422, 1874493440), ('FILE4', 3398, 847872)]
def table(elf):
    return [list(struct.unpack_from('<4I', elf, TAB + 16 * i)) for i in range(N)]
def elf_orig():
    return open(os.path.join(ROOT, 'work', 'SLPS_254.41'), 'rb').read()
def read_entry(t, i, iso=ISO, full=False):
    off, alloc, size, fn = t[i]
    with open(iso, 'rb') as f:
        f.seek(FILES[fn][1] * 2048 + off); return f.read(alloc if full else size)
