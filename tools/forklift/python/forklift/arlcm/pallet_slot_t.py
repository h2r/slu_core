"""LCM type definitions
This file automatically generated by lcm.
DO NOT MODIFY BY HAND!!!!
"""

import cStringIO as StringIO
import struct

class pallet_slot_t(object):
    __slots__ = ["utime", "pos", "size", "dir", "confidence"]

    def __init__(self):
        self.utime = 0
        self.pos = [ 0.0 for dim0 in range(3) ]
        self.size = [ 0.0 for dim0 in range(2) ]
        self.dir = [ 0.0 for dim0 in range(3) ]
        self.confidence = 0.0

    def encode(self):
        buf = StringIO.StringIO()
        buf.write(pallet_slot_t._get_packed_fingerprint())
        self._encode_one(buf)
        return buf.getvalue()

    def _encode_one(self, buf):
        buf.write(struct.pack(">q", self.utime))
        buf.write(struct.pack('>3d', *self.pos[:3]))
        buf.write(struct.pack('>2d', *self.size[:2]))
        buf.write(struct.pack('>3d', *self.dir[:3]))
        buf.write(struct.pack(">d", self.confidence))

    def decode(data):
        if hasattr(data, 'read'):
            buf = data
        else:
            buf = StringIO.StringIO(data)
        if buf.read(8) != pallet_slot_t._get_packed_fingerprint():
            raise ValueError("Decode error")
        return pallet_slot_t._decode_one(buf)
    decode = staticmethod(decode)

    def _decode_one(buf):
        self = pallet_slot_t()
        self.utime = struct.unpack(">q", buf.read(8))[0]
        self.pos = struct.unpack('>3d', buf.read(24))
        self.size = struct.unpack('>2d', buf.read(16))
        self.dir = struct.unpack('>3d', buf.read(24))
        self.confidence = struct.unpack(">d", buf.read(8))[0]
        return self
    _decode_one = staticmethod(_decode_one)

    _hash = None
    def _get_hash_recursive(parents):
        if pallet_slot_t in parents: return 0
        tmphash = (0xa2ddc6175dff49a5) & 0xffffffffffffffff
        tmphash  = (((tmphash<<1)&0xffffffffffffffff)  + (tmphash>>63)) & 0xffffffffffffffff 
        return tmphash
    _get_hash_recursive = staticmethod(_get_hash_recursive)
    _packed_fingerprint = None
    
    def _get_packed_fingerprint():
        if pallet_slot_t._packed_fingerprint is None:
            pallet_slot_t._packed_fingerprint = struct.pack(">Q", pallet_slot_t._get_hash_recursive([]))
        return pallet_slot_t._packed_fingerprint
    _get_packed_fingerprint = staticmethod(_get_packed_fingerprint)

