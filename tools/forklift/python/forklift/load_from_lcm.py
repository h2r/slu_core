from forklift.forkState import ForkState
from lcm_utils import pallet_t_create, object_t_create
from arlcm.pallet_enum_t import pallet_enum_t 
import math
from arlcm.pallet_t import pallet_t 
from arlcm.object_t import object_t 
from arlcm.object_enum_t import object_enum_t
from spatial_features.groundings import PhysicalObject, Prism
from actionMap import ActionMap
import numpy as na

objectTypes = dict()
for key, value in object_enum_t.__dict__.iteritems():
     if not key.startswith("_"):
          objectTypes[value] = key.replace('_', ' ').lower()

palletTypes = dict()
for key, value in pallet_t.__dict__.iteritems():
     if key.startswith("LABEL"):
          label = key.replace('_', ' ').lower()
          label = label.replace('label', '').lstrip()
          palletTypes[value] =  label + " pallet"

def getLabel(obj):
     if isinstance(obj, pallet_t) :
          return palletTypes[obj.label]
     elif isinstance(obj, object_t):
          return objectTypes[obj.object_type.value]
     else:
          return None

def physicalObject(obj, path=None):
     prism = fromLcmObject(obj)

     obj = PhysicalObject(prism, getLabel(obj).split(), path,
                           lcmId=obj.id)
     return obj


def waverly_state_truck():

    state = ForkState.from_lcm(agent=0,orientation=2.0539693267948964,has_pallet=None,
                             pallets=[pallet_t_create(utime=1299426196301667L,id=332652915515583744L,relative_to_id=0,
                                                      pos=(24.756341368702554, 27.852367316177947, -0.97048924996154229),
                                                      orientation=(0.25460500000000003, 0.0, 0.0, -0.96704500000000004),bbox_min=(0.0, 0.0, 0.0),
                                                      bbox_max=(1.0, 1.0, 1.0),num_slot_pairs=0,slot_pairs=[],utime_updated=1299426196301667L,
                                                      last_updated_by=1,approach_lat=42.357270710000002,approach_lon=-71.102750670000006,
                                                      approach_theta=0.51487894550000002,label=13,pallet_type=pallet_enum_t(1)),
                                      pallet_t_create(utime=1299426196693645L,id=332652921296018432L,relative_to_id=0,
                                                      pos=(21.96586766523853, 30.655678756917084, -0.93549230099799763),
                                                      orientation=(0.25156699999999999, 0.0, 0.0, -0.96783999999999981),
                                                      bbox_min=(0.0, 0.0, 0.0),bbox_max=(1.0, 1.0, 1.0),num_slot_pairs=0,
                                                      slot_pairs=[],utime_updated=1299426196693645L,last_updated_by=1,
                                                      approach_lat=42.357297979999998,approach_lon=-71.102782849999997,
                                                      approach_theta=0.50859765040000005,label=7,pallet_type=pallet_enum_t(1)),
                                      pallet_t_create(utime=1299426195755582L,id=332652909006356992L,relative_to_id=0,
                                                      pos=(26.127219483413473, 24.53057638037312, -1.047232909230102),
                                                      orientation=(0.22708600000000007, 0.0, 0.0, -0.97387500000000005),
                                                      bbox_min=(0.0, 0.0, 0.0),bbox_max=(1.0, 1.0, 1.0),num_slot_pairs=0,
                                                      slot_pairs=[],utime_updated=1299426195755582L,last_updated_by=1,
                                                      approach_lat=42.357243060000002,approach_lon=-71.102733420000007,
                                                      approach_theta=0.45816925559999999,label=21,pallet_type=pallet_enum_t(1))],
                             objects=[object_t_create(utime=1299426086211423L,id=332653078070183424L,
                                                      pos=(0.63717945498810913, 30.573454159599919, 0.048958996426324397),
                                                      orientation=(0.99579471000539965, 0.0, 0.0, 0.09161274761332111),
                                                      bbox_min=(0.0, 0.0, -0.40000000000000002),
                                                      bbox_max=(5.3600000000000003, 1.9099999999999999, 0.0),object_type=object_enum_t(5))],
                             actionMap = ActionMap(tmap={0: [0], 1: [1, 2, 3, 4, 5, 6, 7, 8], 2: [1, 2, 3, 4, 5, 6, 7, 8],
                                                                        3: [1, 2, 3, 4, 5, 6, 7, 8], 4: [1, 2, 3, 4, 5, 6, 7, 8],
                                                                        5: [1, 2, 3, 4, 5, 6, 7, 8], 6: [1, 2, 3, 4, 5, 6, 7, 8],
                                                                        7: [1, 2, 3, 4, 5, 6, 7, 8], 8: [1, 2, 3, 4, 5, 6, 7, 8]},
                                                   tmap_locs={0: (19.657631172130511, 14.899825568680297),
                                                              1: [24.567379598930515, 27.17097630397226],
                                                              2: (22.567379598930515, 25.17097630397226),
                                                              3: [21.772630200908406, 29.975488297346931],
                                                              4: (19.772630200908406, 27.975488297346931),
                                                              5: [25.899940887292487, 23.860991529346204],
                                                              6: (23.899940887292487, 21.860991529346204),
                                                              7: [3.0979490301377095, 32.00140307255797],
                                                              8: (1.0979490301377095, 30.00140307255797)}))

    return state, state.actionMap

def quat_pos_to_matrix(quat, pos):

    rot = quat_to_matrix(quat)

    mat = na.zeros(16)
    mat[0] = rot[0];
    mat[1] = rot[1];
    mat[2] = rot[2];
    mat[3] = pos[0];

    mat[4] = rot[3];
    mat[5] = rot[4];
    mat[6] = rot[5];
    mat[7] = pos[1];

    mat[8] = rot[6];
    mat[9] = rot[7];
    mat[10] = rot[8];
    mat[11] = pos[2];

    mat[12] = 0;
    mat[13] = 0;
    mat[14] = 0;
    mat[15] = 1;
    return na.reshape(mat, (4,4))

def quat_to_matrix(quat):
    rot = na.zeros(9)
    
    norm = quat[0]*quat[0] + quat[1]*quat[1] + quat[2]*quat[2] + quat[3]*quat[3]
    if (math.fabs(norm) < 1e-10):
        return rot
        raise ValueError("norm is almost zero: " + `norm`)
    
    norm = 1/norm
    x = quat[1]*norm
    y = quat[2]*norm
    z = quat[3]*norm
    w = quat[0]*norm

    x2 = x*x;
    y2 = y*y;
    z2 = z*z;
    w2 = w*w;
    xy = 2*x*y;
    xz = 2*x*z;
    yz = 2*y*z;
    wx = 2*w*x;
    wy = 2*w*y;
    wz = 2*w*z;

    rot[0] = w2+x2-y2-z2;  rot[1] = xy-wz;  rot[2] = xz+wy;
    rot[3] = xy+wz;  rot[4] = w2-x2+y2-z2;  rot[5] = yz-wx;
    rot[6] = xz-wy;  rot[7] = yz+wx;  rot[8] = w2-x2-y2+z2;

    return rot


def fromLcmObject(obj):
   #x0,y0,z0 = [obj.pos[i] + obj.bbox_min[i] for i in range(3)]
   #x1,y1,z1 = [obj.pos[i] + obj.bbox_max[i] for i in range(3)]
   x0,y0,z0 = [obj.bbox_min[i] for i in range(3)]
   x1,y1,z1 = [obj.bbox_max[i] for i in range(3)]        
   if len(obj.orientation) != 0:
       m = quat_pos_to_matrix(obj.orientation, obj.pos)
       points = na.array([(x0, y0, z0, 1),
                          (x0, y1, z0, 1),
                          (x1, y1, z0, 1),
                          (x1, y0, z1, 1)])

       points_xyz = na.transpose([na.dot(m, p) for p in points])[0:3]
       X, Y, Z = points_xyz

   else:
       xs, ys, zs = obj.pos
       points_xyz = na.transpose([(xs+x0, ys+y0, zs+z0),
                                  (xs+x0, ys+y1, zs+z0),
                                  (xs+x1, ys+y1, zs+z0),
                                  (xs+x1, ys+y0, zs+z0)])
                                 #(x1, y1, z1)])
       Z = [z0, z1]
   return Prism.from_points_xy(points_xyz[0:2], min(Z), max(Z))


def waverly_state_no_truck():
    from lcm_utils import pallet_t_create
    from arlcm.pallet_enum_t import pallet_enum_t 
    state = ForkState.from_lcm(agent=0,orientation=1.4335083267948965,has_pallet=None,objects=[], pallets=[pallet_t_create(utime=1299102507174626L,id=332570240727149312L,relative_to_id=0,pos=(24.412338587288883, 23.106057331055112, -0.92941011292763576),orientation=(0.21585832398088173, 0.0, 0.0, -0.97642469446863367),bbox_min=(0.0, 0.0, 0.0),bbox_max=(1.0, 1.0, 1.0),num_slot_pairs=0,slot_pairs=[],utime_updated=1299102507174626L,last_updated_by=1,approach_lat=42.357234754543896,approach_lon=-71.102755615095504,approach_theta=0.43514158471966757,label=12,pallet_type=pallet_enum_t(1)),pallet_t_create(utime=1299102596014266L,id=332570263432377344L,relative_to_id=0,pos=(20.375941080998292, 30.126415885187956, -0.94472267117867581),orientation=(0.20698039008093438, 0.0, 0.0, -0.97834509153056226),bbox_min=(0.0, 0.0, 0.0),bbox_max=(1.0, 1.0, 1.0),num_slot_pairs=0,slot_pairs=[],utime_updated=1299102596014266L,last_updated_by=1,approach_lat=42.357298591714006,approach_lon=-71.102805219780862,approach_theta=0.41697499973750585,label=21,pallet_type=pallet_enum_t(1)),pallet_t_create(utime=1299102638405780L,id=332570274120938240L,relative_to_id=0,pos=(21.765215070005866, 26.959362372824202, -0.91950706946842298),orientation=(0.29602237423074151, 0.0, 0.0, -0.95518100585951515),bbox_min=(0.0, 0.0, 0.0),bbox_max=(1.0, 1.0, 1.0),num_slot_pairs=0,slot_pairs=[],utime_updated=1299102638405780L,last_updated_by=1,approach_lat=42.357263980902992,approach_lon=-71.102781515660439,approach_theta=0.60105137494768934,label=5,pallet_type=pallet_enum_t(1))], actionMap = ActionMap(rndfFname=None,tmap={0: [0], 1: [1, 2, 3, 4, 5, 6], 2: [1, 2, 3, 4, 5, 6], 3: [1, 2, 3, 4, 5, 6], 4: [1, 2, 3, 4, 5, 6], 5: [1, 2, 3, 4, 5, 6], 6: [1, 2, 3, 4, 5, 6]},tmap_locs={0: (12.927614219589069, 17.70760928202089), 1: [24.169717416007327, 22.441884533914639], 2: (22.169717416007327, 20.441884533914639), 3: [20.121294823865735, 29.466760303256478], 4: (18.121294823865735, 27.466760303256478), 5: [21.63561387870357, 26.26423845456398], 6: (19.63561387870357, 24.26423845456398)}))

#    am = ActionMap(skelFname=None,connectAllNodes=True,manipulation_distance=inf,rndfFname=None,tmap={0: [0], 1: [1, 2, 3, 4, 5, 6], 2: [1, 2, 3, 4, 5, 6], 3: [1, 2, 3, 4, 5, 6], 4: [1, 2, 3, 4, 5, 6], 5: [1, 2, 3, 4, 5, 6], 6: [1, 2, 3, 4, 5, 6]},tmap_locs={0: (12.909535477610628, 17.721409510997436), 1: [24.169772302923125, 22.441893067327189], 2: (22.169772302923125, 20.441893067327189), 3: [20.121349702610928, 29.466768836668887], 4: (18.121349702610928, 27.466768836668887), 5: [21.635668759782639, 26.264246988765635], 6: (19.635668759782639, 24.264246988765635)})
    
    return state, state.actionMap

def fort_lee_two_trucks():
    from lcm_utils import pallet_t_create, object_t_create
    from arlcm.pallet_enum_t import pallet_enum_t 
    state = ForkState.from_lcm(agent=26,orientation=0.45318687843652505,has_pallet=None, pallets=[pallet_t_create(utime=1291316667886630L,id=330574145941659648L,relative_to_id=0,pos=(22.412365180547411, 36.672307249040493, 0.050138581152787069),orientation=(0.97011218763989149, -0.011098229042798155, 0.012197416309175833, 0.24209583998912121),bbox_min=(3.3019999999912212e-06, 8.6614000000014448e-06, 3.3273999996559197e-06),bbox_max=(1.2000032895999999, 1.000008668, 0.70338871259999991),num_slot_pairs=0,slot_pairs=[],utime_updated=1291316667886630L,last_updated_by=8,approach_lat=0.0,approach_lon=0.0,approach_theta=0.0,label=21,pallet_type=pallet_enum_t(6)),pallet_t_create(utime=1291311111264663L,id=330574145942597120L,relative_to_id=0,pos=(19.303553632727262, 46.019574232696023, 0.049978160033206202),orientation=(0.98377892217328278, -0.00015099467559859874, -0.016827400237343033, 0.17859408749853478),bbox_min=(-4.9530000001128975e-06, -0.0096551495999998797, 1.7017999999695385e-06),bbox_max=(1.1999952631999999, 1.0063449266, 1.0287017017999998),num_slot_pairs=0,slot_pairs=[],utime_updated=1291311111264663L,last_updated_by=8,approach_lat=0.0,approach_lon=0.0,approach_theta=0.0,label=6,pallet_type=pallet_enum_t(5)),pallet_t_create(utime=1291305257588353L,id=330574145942618368L,relative_to_id=0,pos=(15.170984984132474, 49.189804927885817, 0.0),orientation=(0.96592582899790735, 0.0, 0.0, 0.25881903499299569),bbox_min=(3.3019999999912212e-06, 8.6614000000014448e-06, 3.3273999996559197e-06),bbox_max=(1.2000032895999999, 1.000008668, 0.70338871259999991),num_slot_pairs=0,slot_pairs=[],utime_updated=0,last_updated_by=0,approach_lat=0.0,approach_lon=0.0,approach_theta=0.0,label=6,pallet_type=pallet_enum_t(6)),pallet_t_create(utime=1291305257588329L,id=330574145942612224L,relative_to_id=0,pos=(18.170991740455097, 49.189804927885817, 0.0),orientation=(0.96592582899790735, 0.0, 0.0, 0.25881903499299569),bbox_min=(3.3019999999912212e-06, 8.6614000000014448e-06, 3.3273999996559197e-06),bbox_max=(1.2000032895999999, 1.000008668, 0.70338871259999991),num_slot_pairs=0,slot_pairs=[],utime_updated=0,last_updated_by=0,approach_lat=0.0,approach_lon=0.0,approach_theta=0.0,label=21,pallet_type=pallet_enum_t(6)),pallet_t_create(utime=1291305257588305L,id=330574145942606080L,relative_to_id=0,pos=(20.330996605657504, 43.459804873270791, 0.0),orientation=(0.96592582899790735, 0.0, 0.0, 0.25881903499299569),bbox_min=(3.3019999999912212e-06, 8.6614000000014448e-06, 3.3273999996559197e-06),bbox_max=(1.2000032895999999, 1.000008668, 0.70338871259999991),num_slot_pairs=0,slot_pairs=[],utime_updated=0,last_updated_by=0,approach_lat=0.0,approach_lon=0.0,approach_theta=0.0,label=21,pallet_type=pallet_enum_t(6))], objects=[object_t_create(utime=1291305257714224L,id=330574145974841600L,pos=(23.432575592772405, 24.999749697299404, 0.29999999999999999),orientation=(0.23127780802830297, 0.0, 0.0, -0.97288775072647693),bbox_min=(-0.24998969560000001, -0.10504134440000003, -0.24998083100000001),bbox_max=(0.25000638339999998, 0.10525112300000003, 0.25000965999999997),object_type=object_enum_t(6)),object_t_create(utime=1291305257714190L,id=330574145974832896L,pos=(23.42166456770385, 23.199293679869204, 0.29999999999999999),orientation=(0.2120432031833574, 0.0, 0.0, -0.97726029285126559),bbox_min=(-0.24998969560000001, -0.10504134440000003, -0.24998083100000001),bbox_max=(0.25000638339999998, 0.10525112300000003, 0.25000965999999997),object_type=object_enum_t(6)),object_t_create(utime=1291305257714265L,id=330574145974851840L,pos=(22.753408063106232, 24.681683694528772, 0.29999999999999999),orientation=(0.97661248691532665, 0.0, 0.0, 0.21500709383892672),bbox_min=(-0.24998969560000001, -0.10504134440000003, -0.24998083100000001),bbox_max=(0.25000638339999998, 0.10525112300000003, 0.25000965999999997),object_type=object_enum_t(6)),object_t_create(utime=1291305257599008L,id=330574145945346304L,pos=(22.298747038423819, 22.483067673549606, 0.84999999999999998),orientation=(0.97305572869864088, 0.0, 0.0, 0.23057005192946656),bbox_min=(6.4008000003768634e-06, -4.064000000041627e-06, -0.4063926848000004),bbox_max=(5.3594067817999997, 1.9151559613999998, 7.4167999998008861e-06),object_type=object_enum_t(5)),object_t_create(utime=1291305257714245L,id=330574145974846976L,pos=(24.078701047653343, 23.498455683481403, 0.29999999999999999),orientation=(0.98162524675128515, 0.0, 0.0, 0.19081895854573377),bbox_min=(-0.24998969560000001, -0.10504134440000003, -0.24998083100000001),bbox_max=(0.25000638339999998, 0.10525112300000003, 0.25000965999999997),object_type=object_enum_t(6)),object_t_create(utime=1291305257714324L,id=330574145974867200L,pos=(9.9374571963655232, 53.394464968465272, 0.29999999999999999),orientation=(0.98162524675128515, 0.0, 0.0, 0.19081895854573377),bbox_min=(-0.24998969560000001, -0.10504134440000003, -0.24998083100000001),bbox_max=(0.25000638339999998, 0.10525112300000003, 0.25000965999999997),object_type=object_enum_t(6)),object_t_create(utime=1291305257714363L,id=330574145974876928L,pos=(9.3220798093142925, 53.083133965297201, 0.29999999999999999),orientation=(0.2120432031833574, 0.0, 0.0, -0.97726029285126559),bbox_min=(-0.24998969560000001, -0.10504134440000003, -0.24998083100000001),bbox_max=(0.25000638339999998, 0.10525112300000003, 0.25000965999999997),object_type=object_enum_t(6)),object_t_create(utime=1291305257714306L,id=330574145974862336L,pos=(9.3553788844454004, 54.76276098170085, 0.29999999999999999),orientation=(0.98652990414240094, 0.0, 0.0, 0.16358101427972985),bbox_min=(-0.24998969560000001, -0.10504134440000003, -0.24998083100000001),bbox_max=(0.25000638339999998, 0.10525112300000003, 0.25000965999999997),object_type=object_enum_t(6)),object_t_create(utime=1291305257714286L,id=330574145974857216L,pos=(8.2097553042197422, 52.337372958383931, 0.84999999999999998),orientation=(0.97305572869864088, 0.0, 0.0, 0.23057005192946656),bbox_min=(6.4008000003768634e-06, -4.064000000041627e-06, -0.4063926848000004),bbox_max=(5.3594067817999997, 1.9151559613999998, 7.4167999998008861e-06),object_type=object_enum_t(5)),object_t_create(utime=1291305257714343L,id=330574145974872064L,pos=(8.6737873491119988, 54.444853978593493, 0.29999999999999999),orientation=(0.97661252886927863, 0.0, 0.0, 0.21500690327417954),bbox_min=(-0.24998969560000001, -0.10504134440000003, -0.24998083100000001),bbox_max=(0.25000638339999998, 0.10525112300000003, 0.25000965999999997),object_type=object_enum_t(6))], actionMap = ActionMap(rndfFname='../../data/directions/forklift/Lee_RNDF_demo.txt',tmap={32: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 33: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 34: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 35: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 36: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 37: set([32, 33, 34, 35, 36, 11, 12, 13, 14, 52, 21, 22, 23, 24, 25, 26, 31]), 11: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 12: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 13: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 14: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 21: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 22: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 23: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 24: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 25: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 26: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52], 31: [31, 32, 33, 34, 35, 36, 21, 22, 23, 24, 25, 26, 12, 14, 13, 11, 52]},tmap_locs={32: (20.355490856707419, 47.58601411282055), 33: (21.68302286950366, 44.917639490130725), 34: (23.010554881040711, 42.249264866643024), 35: (23.541567687164328, 40.247983899614859), 36: (25.134606101760536, 38.802614311787586), 37: (19.431680221194934, 35.790433969970934), 11: (10.443251830809421, 52.366851978978623), 12: (22.391039942239768, 26.350199403631578), 13: (13.806332929157831, 31.6869486498864), 14: (15.576375612893921, 28.351480371473254), 21: (15.133864941960065, 48.364290044963525), 22: (16.018886282569959, 45.251186317967395), 23: (17.346418295370416, 42.582811694480654), 24: (18.673950308169683, 39.91443707177644), 25: (19.204963113037497, 37.913156103953661), 26: (20.798001527639663, 36.467786516913193), 31: (19.470469514842481, 50.476753287655086)}))
    return state, state.actionMap
