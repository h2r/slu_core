"""LCM type definitions
This file automatically generated by lcm.
DO NOT MODIFY BY HAND!!!!
"""

import cStringIO as StringIO
import struct

import object_enum_t

class object_t(object):
    __slots__ = ["utime", "id", "pos", "orientation", "bbox_min", "bbox_max", "object_type"]

    def __init__(self):
        self.utime = 0
        self.id = 0
        self.pos = [ 0.0 for dim0 in range(3) ]
        self.orientation = [ 0.0 for dim0 in range(4) ]
        self.bbox_min = [ 0.0 for dim0 in range(3) ]
        self.bbox_max = [ 0.0 for dim0 in range(3) ]
        self.object_type = None

    def encode(self):
        buf = StringIO.StringIO()
        buf.write(object_t._get_packed_fingerprint())
        self._encode_one(buf)
        return buf.getvalue()

    def _encode_one(self, buf):
        buf.write(struct.pack(">qq", self.utime, self.id))
        buf.write(struct.pack('>3d', *self.pos[:3]))
        buf.write(struct.pack('>4d', *self.orientation[:4]))
        buf.write(struct.pack('>3d', *self.bbox_min[:3]))
        buf.write(struct.pack('>3d', *self.bbox_max[:3]))
        self.object_type._encode_one(buf)

    def decode(data):
        if hasattr(data, 'read'):
            buf = data
        else:
            buf = StringIO.StringIO(data)
        if buf.read(8) != object_t._get_packed_fingerprint():
            raise ValueError("Decode error")
        return object_t._decode_one(buf)
    decode = staticmethod(decode)

    def _decode_one(buf):
        self = object_t()
        self.utime, self.id = struct.unpack(">qq", buf.read(16))
        self.pos = struct.unpack('>3d', buf.read(24))
        self.orientation = struct.unpack('>4d', buf.read(32))
        self.bbox_min = struct.unpack('>3d', buf.read(24))
        self.bbox_max = struct.unpack('>3d', buf.read(24))
        self.object_type = object_enum_t.object_enum_t._decode_one(buf)
        return self
    _decode_one = staticmethod(_decode_one)

    _hash = None
    def _get_hash_recursive(parents):
        if object_t in parents: return 0
        newparents = parents + [object_t]
        tmphash = (0x475fd286e391c128+ object_enum_t.object_enum_t._get_hash_recursive(newparents)) & 0xffffffffffffffff
        tmphash  = (((tmphash<<1)&0xffffffffffffffff)  + (tmphash>>63)) & 0xffffffffffffffff 
        return tmphash
    _get_hash_recursive = staticmethod(_get_hash_recursive)
    _packed_fingerprint = None
    
    def _get_packed_fingerprint():
        if object_t._packed_fingerprint is None:
            object_t._packed_fingerprint = struct.pack(">Q", object_t._get_hash_recursive([]))
        return object_t._packed_fingerprint
    _get_packed_fingerprint = staticmethod(_get_packed_fingerprint)

