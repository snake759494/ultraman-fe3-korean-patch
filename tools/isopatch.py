"""ISO9660 + UDF 브리지 이미지에서 파일 한 개의 위치·크기를 바꾼다(데이터는 호출자가 씀).
PS2 는 ISO9660 디렉터리 레코드로 파일을 찾는다. UDF 파일 엔트리도 같이 맞춰 둔다."""
import struct

SEC = 2048

def _crc16(data):
    crc = 0
    for b in data:
        crc ^= b << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else crc << 1
            crc &= 0xffff
    return crc

def _fix_tag(buf, off, body_len):
    """UDF 서술자 태그(16B)의 CRC·체크섬 재계산."""
    struct.pack_into('<H', buf, off + 8, _crc16(bytes(buf[off + 16:off + 16 + body_len])))
    struct.pack_into('<H', buf, off + 10, body_len)
    s = sum(buf[off + i] for i in range(16) if i != 4) & 0xff
    buf[off + 4] = s

def _both(v):
    return struct.pack('<I', v) + struct.pack('>I', v)

def relocate(f, name, new_lba, new_size, dir_lba=261, dir_secs=1, udf_part=265, udf_fe=range(271, 331)):
    """열린 ISO 파일 f(r+b)에서 루트의 name 을 new_lba/new_size 로."""
    f.seek(dir_lba * SEC); d = bytearray(f.read(dir_secs * SEC)); p = 0; old = None
    while p < len(d) and d[p]:
        nl = d[p + 32]
        if d[p + 33:p + 33 + nl] == name.encode() + b';1':
            old = struct.unpack_from('<I', d, p + 2)[0]
            d[p + 2:p + 10] = _both(new_lba); d[p + 10:p + 18] = _both(new_size)
        p += d[p]
    assert old is not None, name
    f.seek(dir_lba * SEC); f.write(d)
    # UDF 파일 엔트리(태그 261): 짧은 할당 서술자(길이, 위치) 목록
    done = False
    for lba in udf_fe:
        f.seek(lba * SEC); e = bytearray(f.read(SEC))
        if struct.unpack_from('<H', e, 0)[0] != 261: continue
        l_ea, l_ad = struct.unpack_from('<II', e, 168)
        ad = 176 + l_ea
        pos = struct.unpack_from('<I', e, ad + 4)[0]
        if pos + udf_part != old: continue
        # 새 할당: 1GB 조각(0x3FFFF800) 단위로 나눔
        ads = []; rem = new_size; p0 = new_lba - udf_part
        while rem > 0:
            n = min(rem, 0x3FFFF800); ads.append(struct.pack('<II', n, p0)); rem -= n; p0 += n // SEC
        assert len(ads) * 8 <= SEC - ad
        e[ad:ad + l_ad] = bytes(l_ad); e[ad:ad + len(ads) * 8] = b''.join(ads)
        struct.pack_into('<I', e, 172, len(ads) * 8)
        struct.pack_into('<Q', e, 56, new_size)                       # 정보 길이
        struct.pack_into('<Q', e, 64, (new_size + SEC - 1) // SEC)    # 기록된 블록 수
        _fix_tag(e, 0, 176 + l_ea + len(ads) * 8 - 16)
        f.seek(lba * SEC); f.write(e); done = True
        break
    assert done, 'UDF FE not found'

def set_volume_size(f, nsec, udf_part=265):
    f.seek(16 * SEC); p = bytearray(f.read(SEC)); p[80:88] = _both(nsec); f.seek(16 * SEC); f.write(p)
    # UDF 파티션 서술자(태그 5, 주·예비) 길이
    for lba in (34, 50):
        f.seek(lba * SEC); e = bytearray(f.read(SEC))
        if struct.unpack_from('<H', e, 0)[0] == 5:
            struct.pack_into('<I', e, 192, nsec - udf_part)
            _fix_tag(e, 0, struct.unpack_from('<H', e, 10)[0])
            f.seek(lba * SEC); f.write(e)
