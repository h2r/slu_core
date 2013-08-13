"""LCM type definitions
This file automatically generated by lcm.
DO NOT MODIFY BY HAND!!!!
"""

import cStringIO as StringIO
import struct
class task_type_enum_t(object):
    __slots__ = [ "value" ]
    DESTINATION_CHECKPOINT = 1
    DESTINATION_POSE = 2
    PALLET_MANIPULATION = 3
    _packed_fingerprint = struct.pack(">Q", 0xb1ddb17c4b77e851)

    def __init__ (self, value):
        self.value = value

    def _get_hash_recursive(parents):
        return 0xb1ddb17c4b77e851
    _get_hash_recursive=staticmethod(_get_hash_recursive)
    def _get_packed_fingerprint():
        return task_type_enum_t._packed_fingerprint
    _get_packed_fingerprint = staticmethod(_get_packed_fingerprint)

    def encode(self):
        return struct.pack(">Qi", 0xb1ddb17c4b77e851, self.value)
    def _encode_one(self, buf):
        buf.write (struct.pack(">i", self.value))

    def decode(data):
        if hasattr (data, 'read'):
            buf = data
        else:
            buf = StringIO.StringIO(data)
        if buf.read(8) != task_type_enum_t._packed_fingerprint:
            raise ValueError("Decode error")
        return task_type_enum_t(struct.unpack(">i", buf.read(4))[0])
    decode = staticmethod(decode)
    def _decode_one(buf):
        return task_type_enum_t(struct.unpack(">i", buf.read(4))[0])
    _decode_one = staticmethod(_decode_one)

