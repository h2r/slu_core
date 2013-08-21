import matplotlib_qt
import unittest
from g3.inference.gui import costFunctionBrowser
from forklift import forkState
from forklift.forkState import PickUp
import basewindow
from environ_vars import SLU_HOME
from g3.cost_functions.cost_function_crf import CostFnCrf
#from g3.inference import esdcSearch
from g3.inference import nodeSearch
import spatial_features_cxx as sf
from forklift.load_from_lcm import waverly_state_truck

cfb = None
app = None
def initialize():
    global app
    global cfb
    if app != None:
        return
    
    app = basewindow.makeApp()
    state, am = waverly_state_truck()

    if cfb and state == cfb.state:
        return

    tp = nodeSearch.BeamSearch(CostFnCrf.from_mallet("%s/tools/crf_training/models/crf_discrete_forklift_1.5.pck" % SLU_HOME), useRrt=False)

    cfb = costFunctionBrowser.MainWindow(
        [10, 40, 10, 40],
        tp, show_gui=False)
    print 'updating state'
    cfb.setState(state)

    #parameters
    cfb.beamWidthBox.setValue(2)
    cfb.seqBeamWidthBox.setValue(10)
    cfb.searchDepthBox.setValue(3)
    cfb.selectEsdcExtractor()
    print 'starting tests'


class TestCase(unittest.TestCase):
    def __init__(self, *args, **margs):
        unittest.TestCase.__init__(self, *args, **margs)
        basewindow.batch_mode = True
        initialize()
        global cfb
        self.cfb = cfb


    def testPickUpWaverly(self):
        esdcs, plans = self.cfb.followCommand("Pick up the tire pallet.")
        plan = plans[0]
        ggg = plan.ggg
        state = plan.state
        eventNode = [node for node in ggg.nodes if "EVENT" in node.type][0]
        print "factors", eventNode.factors
        objectNode = eventNode.factors[0].nodes_for_link("l")[0]

        hopefullyTire = ggg.evidences[objectNode.id][0]
        sequence = state.getSequence()
        print "sequence", sequence
        heldPallets = [action.pallet_id for s, action in sequence if isinstance(action, PickUp)]
        for splan in plans:
            print splan.cost, '-----------'
            print [a for s,a in splan.state.getSequence()]
            break
        self.assertEqual(hopefullyTire.tags, ("tire", "assembly", "pallet"))
        print "tags", hopefullyTire.tags
        print "held", heldPallets
        self.assertTrue(hopefullyTire.lcmId in heldPallets)

    def testPickUpBoxWaverly(self):
        esdcs, plans = self.cfb.followCommand("Pick up the box pallet.")
        plan = plans[0]
        ggg = plan.ggg
        state = plan.state
        eventNode = [node for node in ggg.nodes if "EVENT" in node.type][0]
        print "factors", eventNode.factors
        objectNode = eventNode.factors[0].nodes_for_link("l")[0]

        hopefullyBox = ggg.evidences[objectNode.id][0]
        sequence = state.getSequence()
        heldPallets = [action.pallet_id for s, action in sequence if isinstance(action, PickUp)]
        for splan in plans:
            print splan.cost, '-----------'
            print [a for s,a in splan.state.getSequence()]
            break
        self.assertNotEqual(hopefullyBox.tags, ("tire", "assembly", "pallet"))
        

        print "tags", hopefullyBox.tags
        self.assertTrue(hopefullyBox.lcmId in heldPallets)


    
    def testPutWaverly(self):

        esdcs, plans = self.cfb.followCommand("Put the tire pallet on the truck.")
        #self.cfb.show()

        plan = plans[0]
        state = plan.state
        ggg = plan.ggg

        eventNode = [node for node in ggg.nodes if "EVENT" in node.type][0]
        objectNode = eventNode.factors[0].nodes_for_link("l")[0]
        placeNode = eventNode.factors[0].nodes_for_link("l2")[0]
        truckNode = placeNode.factors[1].nodes_for_link("l")[0]

        print 'Node ids:',objectNode.id, placeNode.id, truckNode.id
        hopefullyTire = ggg.evidences[objectNode.id][0]
        hopefullyTruck = ggg.evidences[truckNode.id][0]

        self.assertEqual(hopefullyTire.tags, ("tire", "assembly", "pallet"))
        self.assertEqual(hopefullyTruck.tags, ("flatbed", "trailer"))
        place = ggg.evidences[placeNode.id][0]
        #self.assertTrue(sf.math3d_supports(hopefullyTruck.prismAtT(-1), hopefullyTire.prismAtT(-1)))
        self.assertTrue(sf.math3d_supports(hopefullyTruck.prismAtT(-1), place.prismAtT(-1)))

        self.assertTrue(sf.math3d_intersect_prisms(hopefullyTruck.prismAtT(-1), place.prismAtT(-1)))
        # self.assertTrue(state.get_held_pallet() == None)

    
    def testGoWaverly(self):
        esdcs, plans = self.cfb.followCommand("Go to the trailer.")
        
        plan = plans[0]
        state = plan.state
        ggg = plan.ggg

        agent = state.agent

        eventNode = [node for node in ggg.nodes if "EVENT" in node.type][0]
        pathNode = eventNode.factors[0].nodes_for_link("l")[0]
        truckNode = pathNode.factors[1].nodes_for_link("l")[0]

        print truckNode
        hopefullyTruck = ggg.evidences[truckNode.id][0]

        dist = sf.math2d_dist(agent.prismAtT(-1).centroid2d(), 
                              hopefullyTruck.prismAtT(-1).centroid2d())

        self.assertEqual(hopefullyTruck.tags, ('flatbed', 'trailer'))
        #self.assertTrue(dist < 3, dist)
        

    def testGoNear(self):
        esdcs, plans = self.cfb.followCommand("Go to the tire pallet near the truck.")
        
        plan = plans[0]
        state = plan.state
        ggg = plan.ggg


        eventNode = [node for node in ggg.nodes if "EVENT" in node.type][0]
        pathNode = eventNode.factors[0].nodes_for_link("l")[0]
        palletNode = pathNode.factors[1].nodes_for_link("l")[0]

        hopefullyPallet = ggg.evidences[palletNode.id][0]
        
        self.assertTrue("pallet" in hopefullyPallet.tags)



        
