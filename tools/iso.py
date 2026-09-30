"""ISO 읽기 도우미 (pycdlib 기반 파일 목록)."""
import os, pycdlib
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ISO = os.path.join(ROOT, 'Ultraman - Fighting Evolution 3 (Japan).iso')
def listing(iso=ISO):
    p = pycdlib.PyCdlib(); p.open(iso); out = []
    for dp, dirs, files in p.walk(iso_path='/'):
        for f in files:
            path = (dp.rstrip('/') + '/' + f)
            rec = p.get_record(iso_path=path)
            out.append((path, rec.extent_location(), rec.data_length))
    p.close(); return out
def read(lba, size, iso=ISO):
    with open(iso, 'rb') as f:
        f.seek(lba * 2048); return f.read(size)
if __name__ == '__main__':
    for p, l, s in sorted(listing(), key=lambda x: x[1]): print(f'{l:8d} {s:11d} {p}')
