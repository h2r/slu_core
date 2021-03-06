"""LCM type definitions
This file automatically generated by lcm.
DO NOT MODIFY BY HAND!!!!
"""

import cStringIO as StringIO
import struct

import pointlist2d_t

import botlcm.pose_t

class pallet_manipulation_command_t(object):
    __slots__ = ["utime", "destination_id", "task_id", "pickup", "pallet_id", "roi_utime", "camera", "pose", "roi", "image_utime"]

    PALLET_ID_UNKNOWN = -1

    def __init__(self):
        self.utime = 0
        self.destination_id = 0
        self.task_id = 0
        self.pickup = False
        self.pallet_id = 0
        self.roi_utime = 0
        self.camera = ""
        self.pose = None
        self.roi = None
        self.image_utime = 0

    def encode(self):
        buf = StringIO.StringIO()
        buf.write(pallet_manipulation_command_t._get_packed_fingerprint())
        self._encode_one(buf)
        return buf.getvalue()

    def _encode_one(self, buf):
        buf.write(struct.pack(">qqqbqq", self.utime, self.destination_id, self.task_id, self.pickup, self.pallet_id, self.roi_utime))
        __camera_encoded = self.camera.encode('utf-8')
        buf.write(struct.pack('>I', len(__camera_encoded)+1))
        buf.write(__camera_encoded)
        buf.write("\0")
        self.pose._encode_one(buf)
        self.roi._encode_one(buf)
        buf.write(struct.pack(">q", self.image_utime))

    def decode(data):
        if hasattr(data, 'read'):
            buf = data
        else:
            buf = StringIO.StringIO(data)
        if buf.read(8) != pallet_manipulation_command_t._get_packed_fingerprint():
            raise ValueError("Decode error")
        return pallet_manipulation_command_t._decode_one(buf)
    decode = staticmethod(decode)

    def _decode_one(buf):
        self = pallet_manipulation_command_t()
        self.utime, self.destination_id, self.task_id, self.pickup, self.pallet_id, self.roi_utime = struct.unpack(">qqqbqq", buf.read(41))
        __camera_len = struct.unpack('>I', buf.read(4))[0]
        self.camera = buf.read(__camera_len)[:-1].decode('utf-8')
        self.pose = botlcm.pose_t._decode_one(buf)
        self.roi = pointlist2d_t.pointlist2d_t._decode_one(buf)
        self.image_utime = struct.unpack(">q", buf.read(8))[0]
        return self
    _decode_one = staticmethod(_decode_one)

    _hash = None
    def _get_hash_recursive(parents):
        if pallet_manipulation_command_t in parents: return 0
        newparents = parents + [pallet_manipulation_command_t]
        tmphash = (0x7c046770f827d2f1+ botlcm.pose_t._get_hash_recursive(newparents)+ pointlist2d_t.pointlist2d_t._get_hash_recursive(newparents)) & 0xffffffffffffffff
        tmphash  = (((tmphash<<1)&0xffffffffffffffff)  + (tmphash>>63)) & 0xffffffffffffffff 
        return tmphash
    _get_hash_recursive = staticmethod(_get_hash_recursive)
    _packed_fingerprint = None
    
    def _get_packed_fingerprint():
        if pallet_manipulation_command_t._packed_fingerprint is None:
            pallet_manipulation_command_t._packed_fingerprint = struct.pack(">Q", pallet_manipulation_command_t._get_hash_recursive([]))
        return pallet_manipulation_command_t._packed_fingerprint
    _get_packed_fingerprint = staticmethod(_get_packed_fingerprint)

