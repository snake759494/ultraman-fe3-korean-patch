"""FUM 묶음: 'FUM\0', u32 개수, 항목 0x80B씩 [이름 0x74][오프셋][할당크기][실제크기]."""
import struct
def parse(d):
    assert d[:4] == b'FUM\0'
    n = struct.unpack_from('<I', d, 4)[0]; out = []
    for i in range(n):
        b = 8 + 0x80 * i
        name = d[b:b + 0x74].split(b'\0')[0].decode('ascii')
        off, alloc, size = struct.unpack_from('<3I', d, b + 0x74)
        out.append((name, off, alloc, size))
    return out
def members(d):
    return [(n, d[o:o + s]) for n, o, a, s in parse(d)]
