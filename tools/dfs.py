"""DFS\x01 압축 (오쿠무라 LZSS: 링 4096, 시작 0xFEE, 플래그 LSB부터 1=리터럴, 짝 = 오프셋12비트|길이4비트+3).
헤더: 'DFS\x01', u32 풀린 크기, u32 전체 파일 크기."""
import struct
def decompress(d):
    assert d[:4] == b'DFS\x01', d[:4]
    usize, csize = struct.unpack_from('<II', d, 4)
    ring = bytearray(4096); r = 0xFEE; out = bytearray(); i = 12; flags = 0
    while len(out) < usize and i < len(d):
        flags >>= 1
        if not flags & 0x100:
            flags = d[i] | 0xFF00; i += 1
        if i >= len(d): break
        if flags & 1:
            c = d[i]; i += 1; out.append(c); ring[r] = c; r = (r + 1) & 0xFFF
        else:
            if i + 1 >= len(d): break
            a, b = d[i], d[i + 1]; i += 2
            o = a | ((b & 0xF0) << 4); n = (b & 0xF) + 3
            for k in range(n):
                c = ring[(o + k) & 0xFFF]; out.append(c); ring[r] = c; r = (r + 1) & 0xFFF
    return bytes(out[:usize])
def compress(data):
    """탐욕 LZSS 압축 (해시 체인). 게임 해제기와 호환."""
    ring = bytearray(4096); r = 0xFEE
    out = bytearray(b'DFS\x01' + b'\0' * 8)
    n = len(data); i = 0
    # 링 버퍼 대신 입력 위치 기반 탐색 (거리 < 4096-18 이면 링 위치 = (0xFEE + pos) & 0xFFF)
    head = {}
    while i < n:
        flagpos = len(out); out.append(0); flag = 0
        for bit in range(8):
            if i >= n: break
            best = 0; bpos = 0
            if i + 3 <= n:
                key = data[i:i + 3]
                cand = head.get(key)
                if cand:
                    for p in reversed(cand[-64:]):
                        if i - p >= 4096 - 18: break
                        l = 0; mx = min(18, n - i)
                        while l < mx and data[p + l] == data[i + l]: l += 1
                        if l > best:
                            best = l; bpos = p
                            if l == 18: break
            if best >= 3:
                o = (0xFEE + bpos) & 0xFFF
                out += bytes([o & 0xFF, ((o >> 4) & 0xF0) | (best - 3)])
                step = best
            else:
                flag |= 1 << bit; out.append(data[i]); step = 1
            for k in range(step):
                if i + k + 3 <= n: head.setdefault(data[i + k:i + k + 3], []).append(i + k)
            i += step
        out[flagpos] = flag
    struct.pack_into('<II', out, 4, n, len(out))
    return bytes(out)
