"""SLPS_254.41 간이 역어셈블: python tools/dis.py <vaddr hex> <개수>"""
import sys, os, capstone
d = open(os.path.join(os.path.dirname(__file__), '..', 'work', 'SLPS_254.41'), 'rb').read()
BASE = 0x200000 - 0x1000  # vaddr = fileoff + BASE
md = capstone.Cs(capstone.CS_ARCH_MIPS, capstone.CS_MODE_MIPS64 + capstone.CS_MODE_LITTLE_ENDIAN); md.skipdata = True
def dis(va, n):
    fo = va - BASE
    for i in md.disasm(d[fo:fo + n * 4], va):
        print('%08x  %s %s' % (i.address, i.mnemonic, i.op_str))
if __name__ == '__main__':
    dis(int(sys.argv[1], 16), int(sys.argv[2]))
