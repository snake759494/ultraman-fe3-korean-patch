"""원본 ISO 의 해시를 확인하고 xdelta 를 적용한 뒤 결과 해시까지 검사한다.

사용:
  python tools/apply_release.py --xdelta <xdelta3.exe> --source "Ultraman - Fighting Evolution 3 (Japan).iso" --patch UltramanFE3_PS2_KO_v1.0.xdelta --output "Ultraman - Fighting Evolution 3 (Japan) (Korean).iso"

기존 출력 파일은 덮어쓰지 않는다. 원본·패치·결과 중 하나라도 해시가 다르면 실패로 끝낸다.
"""
import argparse, hashlib, os, subprocess, sys

SOURCE_SIZE = 2811789312
SOURCE_SHA256 = "54b801de3fb5d0185c822bfadd47d49d19c9fdba7d9ca8246a8a1eb8f3ae57bd"
PATCH_SHA256 = "8337162036c224a3497ef85f143232ee5f9a65aac33fa323f4f2a9546848d2cd"
OUTPUT_SIZE = 2811789312
OUTPUT_SHA256 = "52412e4f08f21ae91a3e90f564e7a5725a62cf21a706bf2c702e21228025b0a9"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 24), b""):
            h.update(block)
    return h.hexdigest()


def check(label, path, size, digest):
    n = os.path.getsize(path)
    if size is not None and n != size:
        print(f"{label}: 크기 {n:,} != {size:,}"); return False
    d = sha256(path)
    if d != digest:
        print(f"{label}: SHA-256 불일치\n  실제 {d}\n  기대 {digest}"); return False
    print(f"{label}: OK ({n:,} B)")
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--xdelta", required=True, help="xdelta3 실행 파일")
    ap.add_argument("--source", required=True, help="수정되지 않은 일본판 ISO")
    ap.add_argument("--patch", required=True, help="릴리즈 xdelta")
    ap.add_argument("--output", required=True, help="만들 한글판 ISO")
    a = ap.parse_args()
    if os.path.exists(a.output):
        sys.exit("출력 파일이 이미 있습니다: " + a.output)
    if not check("원본", a.source, SOURCE_SIZE, SOURCE_SHA256): sys.exit(1)
    if not check("패치", a.patch, None, PATCH_SHA256): sys.exit(1)
    r = subprocess.run([a.xdelta, "-d", "-s", a.source, a.patch, a.output])
    if r.returncode != 0:
        sys.exit("xdelta 적용 실패")
    if not check("결과", a.output, OUTPUT_SIZE, OUTPUT_SHA256): sys.exit(1)
    print("완료")


if __name__ == "__main__":
    main()
