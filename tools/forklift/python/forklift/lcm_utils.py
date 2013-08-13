from arlcm.pallet_t import pallet_t 
from arlcm.object_t import object_t 

def pallet_t_create(**args):

    pallet = pallet_t()
    for key in pallet_t.__slots__:
        exec "pallet.%s = args[key]" % key

    return pallet

def pallet_enum_t_repr(pt):
    return "pallet_enum_t(" + repr(pt.value) + ")"

def pallet_t_repr(pallet):
    args = []
    for key in pallet_t.__slots__:
        if key != "pallet_type":
            args.append(key + "=" + repr(eval("pallet.%s" % key)))

    args.append("pallet_type=" + pallet_enum_t_repr(pallet.pallet_type))

    result = "pallet_t_create(" + ",".join(args) + ")"
    return result






def object_t_create(**args):

    object = object_t()
    for key in object_t.__slots__:
        exec "object.%s = args[key]" % key

    return object

def object_enum_t_repr(pt):
    return "object_enum_t(" + repr(pt.value) + ")"

def object_t_repr(object):
    args = []
    for key in object_t.__slots__:
        if key != "object_type":
            args.append(key + "=" + repr(eval("object.%s" % key)))

    args.append("object_type=" + object_enum_t_repr(object.object_type))

    result = "object_t_create(" + ",".join(args) + ")"
    return result



