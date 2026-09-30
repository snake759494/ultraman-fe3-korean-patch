"""원본 ISO 에서 실행파일(work/SLPS_254.41)과 FILE1/FILE4 항목(work/ext/NNNN.bin)을 꺼낸다.
FUM 묶음은 마지막 멤버가 색인의 '실제크기'를 넘으므로 할당크기까지 읽는다."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from iso import read, ROOT
import ftab

def main():
    work = os.path.join(ROOT, 'work'); ext = os.path.join(work, 'ext')
    os.makedirs(ext, exist_ok=True)
    open(os.path.join(work, 'SLPS_254.41'), 'wb').write(read(356, 2979640))
    t = ftab.table(ftab.elf_orig())
    n = 0
    for i in range(ftab.N):
        if t[i][3] not in (0, 3): continue   # FILE2/FILE3 의 동영상·음성은 쓰지 않음
        d = ftab.read_entry(t, i)
        if d[:4] == b'FUM\0': d = ftab.read_entry(t, i, full=True)
        open(os.path.join(ext, '%04d.bin' % i), 'wb').write(d); n += 1
    print('항목', n)

if __name__ == '__main__':
    main()
