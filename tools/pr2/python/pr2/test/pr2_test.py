
import unittest
from g3.inference.gui import costFunctionBrowser
from pr2.pr2_state import Pr2State
import basewindow
from environ_vars import SLU_HOME
from g3.cost_functions.cost_function_crf import CostFnCrf
#from g3.inference import esdcSearch
from g3.inference import nodeSearch


cfb = None
app = None
def initialize():
    global app
    global cfb
    if app != None:
        return
    
    app = basewindow.makeApp()
    state = Pr2State.init_state()

    if cfb and state == cfb.state:
        return

    tp = nodeSearch.BeamSearch(CostFnCrf.from_mallet("%s/data/directions/direction_training/annotation/models/crf_discrete_pr2_1.5.pck" % SLU_HOME), useRrt=False)

    cfb = costFunctionBrowser.MainWindow(
        [10, 40, 10, 40],
        tp, show_gui=False)
    print 'updating state'
    cfb.setState(state)

    #parameters
    cfb.beamWidthBox.setValue(2)
    cfb.seqBeamWidthBox.setValue(10)
    cfb.searchDepthBox.setValue(3)
    print 'starting tests'


class TestCase(unittest.TestCase):
    def __init__(self, *args, **margs):
        unittest.TestCase.__init__(self, *args, **margs)
        basewindow.batch_mode = True
        initialize()
        global cfb
        self.cfb = cfb


    def testPickUpRedBlockWaverly(self):
        esdcs, plans = self.cfb.followCommand("Pick up the red block.")
        plan = plans[0]
        ggg = plan.ggg
        eventNode = [node for node in ggg.nodes if "EVENT" in node.type][0]
        print "factors", eventNode.factors
        objectNode = eventNode.factors[0].nodes_for_link("l")[0]

        hopefullyRed = ggg.evidences[objectNode.id][0]
        self.assertEqual(hopefullyRed.tags, ("red", "block"))

    def testPickUpBlueBlock(self):
        esdcs, plans = self.cfb.followCommand("Pick up the blue block.")
        plan = plans[0]
        ggg = plan.ggg
        eventNode = [node for node in ggg.nodes if "EVENT" in node.type][0]
        print "factors", eventNode.factors
        objectNode = eventNode.factors[0].nodes_for_link("l")[0]

        hopefullyRed = ggg.evidences[objectNode.id][0]
        self.assertEqual(hopefullyRed.tags, ("blue", "block"))


    
