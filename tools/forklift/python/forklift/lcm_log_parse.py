import lcm
import sys

class LcmParse:

    def __init__(self):
        self.agent_obj = None
        self.object_id_to_path = dict()
        self.pobjs = []

    def get_path(self, lcm_obj):
        return self.object_id_to_path[lcm_obj.id]

def trimLog(inLog, outLog, numMsgs=15000):
    log = lcm.EventLog(inLog, "r")
    new_log = lcm.EventLog(outLog, 'w', overwrite=True)
    
    msg_types = ["POSE", "PALLET_LIST", "GPS_TO_LOCAL", "OBJECT_LIST"]

    for i, e in enumerate(log):
        
        if e.channel in msg_types:
            new_log.write_event(e.timestamp, e.channel, e.data)
        else:
            continue

        if i > numMsgs:
            new_log.close()
            return

if __name__ == "__main__":
    trimLog(sys.argv[1], sys.argv[2])
