import lcm
import action_executor
import rndf_util as ru
from forklift import forkState
import spatial_features_cxx as sf
from na import transpose

def planToLcmLog(state, ggg, fname, rndf, app=None, 
                 realForklift=False):
    if app == None:
        app = action_executor.App(rndf_file=rndf)

    sequence = state.getSequence()
    
    log = lcm.EventLog(fname, 'w', overwrite=True)

    sx, sy, sz, stheta = state.getGroundableById(state.getAgentId()).path.points_ptsztheta[0]

    #if actionMap != None:
    #    startId = actionMap.nearest_index((sx, sy))
    #    for chk_pt in rndf.checkpoints:
    #        if chk_pt.id_int == startId:
    #            lat = chk_pt.waypoint.lat
    #            lon = chk_pt.waypoint.lon
    #            break
    #else:
    lat, lon = ru.xy_to_latlon(sx, sy, rndf.origin)

    if not realForklift:
        transportEvent = app.send_transport_msg(lat, lon, stheta, returnEvent=True)
        log.write_event(transportEvent.timestamp, transportEvent.channel, transportEvent.data)

    for s, action in sequence:
        print action
        events = []
        if isinstance(action, forkState.Move):
            #event = app.send_checkpoint(a.to_loc, returnEvent=True)
            sx, sy = action.from_location[0:2]
            x, y = action.to_location[0:2]
            
            #To keep forklift from trying to get to close to a pallet    
            line = sf.math2d_step_along_line([(x,sx),(y,sy)], .1)
            line_pts = transpose(line)
            worstCase = True # worst case if all points along line are too close to pallets
            bestX = x
            bestY = y
            maxMinDist = 0 # distance for the point with greatest buffer (infinum)
            for px, py in line_pts:
                tooClose = False
                held_pallet = s.get_held_pallet()

                localMinDist = 100 # keeps track of the distance to closest pallet for this (px, py)
                for obj in [s.getGroundableById(gid) for gid in s.getObjectsSet()]:
                    if held_pallet and obj.lcmId == held_pallet.lcmId:
                        continue
                    distFromPallet = sf.math2d_dist((px, py), obj.prismAtT(-1).centroid2d())
                    if distFromPallet < localMinDist:
                        localMinDist = distFromPallet

                    if distFromPallet < 4.0:
                        tooClose = True
                        break
                if not tooClose:
                    bestX = px
                    bestY = py
                    print 'changing move from', (x,y), 'to', (bestX, bestY)
                    worstCase = False
                    break
                elif localMinDist > maxMinDist: # does this (px, py) offer a better worst case buffer?
                    maxMinDist = localMinDist
                    bestX = px
                    bestY = py

            # If none of the points were sufficiently far from the pallet, choose the one that was the farthest
            if worstCase == True:
                print '(px, py) farthest from pallet was ', maxMinDist, ' away. Changing from', (x,y), 'to', (bestX, bestY)

            px = bestX
            py = bestY

            lat, lon = ru.xy_to_latlon(px,py, rndf.origin)
            events.append(app.send_latlon(lat, lon, returnEvent = True))

        elif isinstance(action, forkState.Place):
            x,y,z = action.location
            lat,lon = ru.xy_to_latlon(x,y, rndf.origin)
            
            if realForklift:
                print "**************************************"
                print "WARNING--sending to forklift checkpoint 16"
                print "this is a hack and only applies at waverly"
                print "long term, agile should probably be changed to"
                print "handle long distance \"place\" commands without"
                print "having to go to a checkpoint first."
                events.append(app.send_checkpoint(16, returnEvent = True))

            events.append(app.send_place_pallet_msg(lat, lon, z, returnEvent=True))
        elif isinstance(action, forkState.Pickup):
            print "pallet", action.pallet_id
            
            if action.pallet_id == -1:
                print "************************************"
                print "warning, overwriting pallet id", action.pallet_id
                print "remove me after we figure out why it is -1."
                print "we are hardcoding it to the correct ID in one specific"
                print "scenario, but this does not generalize."
                
                pallet_id = 330225303595152896
            else:
                pallet_id = action.pallet_id
            
            events.append(app.send_pickup_pallet_msg(pallet_id, returnEvent=True))
        elif action == None: 
            continue
        else:
            raise TypeError('Unrecognized action: ' + `action` + " class: " +
                            `action.__class__`)
        
        for event in events:
            log.write_event(event.timestamp, event.channel, event.data)
    log.close()
