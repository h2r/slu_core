from arlcm.pallet_t import pallet_t
from arlcm.object_t import object_t

from rndf_util import rndf
import forkState, state_extractor
from arlcm.object_enum_t import object_enum_t


def create_world_lee():
    rndf_map = "../../data/directions/forklift/Lee_RNDF_demo.txt"
    log = "../../data/directions/forklift/logs/go_to_receiving.lcmlog"
    return state_extractor.getInitialStateFromLogApp(log, rndf_file=rndf_map)

def create_world_waverly():
    rndf_map = "../../data/directions/forklift/Lee_at_Waverly_RNDF_onezone.txt"
    log = "../../data/directions/forklift/logs/waverly_real_truck.lcmlog"
    return state_extractor.getInitialStateFromLogApp(log, rndf_file=rndf_map)
