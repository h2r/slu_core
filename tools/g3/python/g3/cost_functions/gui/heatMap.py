import matplotlib_qt
from forklift.forkState import waverly_state_truck
from esdcs.groundings import assignPathGroundings, Prism, Place, Path, PhysicalObject
from esdcs.gui.drawUtils import drawObject
from esdcs.dataStructures import ExtendedSdcGroup
from esdcs.esdcIo.annotationIo import Annotation
from esdcs.extractor.stanfordParserExtractor import Extractor
import numpy as na
from numpy import transpose as tp
from forklift.forkState import prism_from_point
from g3.cost_functions.cost_function_crf import CostFnCrf
from optparse import OptionParser
import basewindow 
from g3.cost_functions.gui import crfFeatureWeights
import math
from g3.esdcs_to_ggg import ggg_from_esdc
from g3.annotation_to_ggg import annotation_to_ggg_map
from g3.graph import GGG, Evidences
import copy
import spatial_features_cxx as sf

def initial_annotation(state, esdc):
    esdcs = ExtendedSdcGroup([esdc])

         
    ax, ay = state.getPosition()
    agent_prism  = prism_from_point(ax, ay, 0, 1)
    agent_object = PhysicalObject(agent_prism, [], 
                                  Path([1], [[ax], [ay], [0], [state.orientation]]), 
                                  lcmId=state.getAgentId())
    context = state.to_context()
    context.agent = agent_object
    annotation = Annotation(0, esdcs, context=context, agent=agent_object)
    
    #peg figure of event to agent
    fig = esdc.f[0]
    annotation.setGrounding(fig, agent_object)
    
    return annotation


def annotation_copy(annotation):
     objectGroundings = []
     for esdc in annotation.flattenedEsdcs:
          groundings = annotation.getGroundings(esdc)
          objectGroundings.append(copy.deepcopy(groundings))
          
     newAnnotation = Annotation(0, annotation.esdcs, objectGroundings)
     a = annotation.agent
     newAnnotation.agent = PhysicalObject(a.prism, a.tags, a.path, a.lcmId)
     newAnnotation.priorAnnotation = annotation.priorAnnotation
     newAnnotation.context = annotation.context
     
     return newAnnotation

def drawPlaceCostMap(featureBrowser, physicalObject, esdc, annotation, 
                     beam_search, xmin, xmax, ymin, ymax, step):

    obj = physicalObject
    Xs = obj.pX - obj.pX[0]
    Ys = obj.pY - obj.pY[0]
    zStart = obj.zStart
    zEnd = obj.zEnd
    cx, cy = obj.centroid2d()
    dx, dy = cx - obj.pX[0], cy - obj.pY[0]

    costs = na.zeros((int((ymax-ymin)/step), int((xmax-xmin)/step)))
    annotations = []
    print dx, dy
    path = Path([0], [[(xmax - xmin)*0.5],
                      [(ymax - ymin)*0.5],
                      [0], 
                      [0]])
    
    
    for i, x in enumerate(na.arange(xmin, xmax, step)):
        for j, y in enumerate(na.arange(ymin, ymax, step)):

            prism = Prism([Xs + x - dy, Ys + y - dx], zStart, zEnd)

            place = Place(prism)
            
            new_annotation = annotation_copy(annotation)
            new_annotation.setGrounding(esdc, place)
            new_annotation.setGroundingIsCorrect(esdc, True)
            #new_annotation.agent.setPath(path)
            state, gggs = annotation_to_ggg_map(new_annotation)
            #ggg = ggg_from_esdc(new_annotation.esdcs[0])
            ggg = gggs[esdc]
            factor = ggg.esdc_to_factor(esdc)

            new_evidences = ggg.evidences
            for phi in factor.nodes_with_type("phi"):
                new_evidences = new_evidences.set_evidence(phi.id, True)
            ggg = GGG.from_ggg_and_evidence(ggg, new_evidences)

            cost, entries = beam_search.cf_obj.costEntry([factor], state, 
                                                         ggg)

            costs[j][i] = math.exp(-1.0*cost)
            annotations.append(((x,y), entries))

    #axes.imshow(costs, origin="lower",
    #            extent=(xmin, xmax, ymin, ymax))
    featureBrowser.setCostImage(costs, annotations, xmin, xmax, ymin, ymax)

def drawGroundingCostMap(featureBrowser, physicalObject, esdc, annotation, beam_search, xmin, xmax, ymin, ymax, step):

    obj = physicalObject
    Xs = obj.X - obj.X[0]
    Ys = obj.Y - obj.Y[0]
    zStart = obj.prism.zStart
    zEnd = obj.prism.zEnd

    costs = na.zeros((int((ymax-ymin)/step), int((xmax-xmin)/step)))
    annotations = []

    for i, x in enumerate(na.arange(xmin, xmax, step)):
        for j, y in enumerate(na.arange(ymin, ymax, step)):
            prism = Prism([Xs+x, Ys+y], zStart, zEnd)
            new_object = PhysicalObject(prism, obj.tags)
            
            new_annotation = annotation_copy(annotation)
            new_annotation.setGrounding(esdc, new_object)
            cost, entries = beam_search.cf_obj.costEntry([esdc], new_annotation)
#            print j, i, len(costs), len(costs[j])
            costs[j][i] = math.exp(-1.0*cost)
            annotations.append(((x,y), entries))

    featureBrowser.setCostImage(costs, annotations, xmin, xmax, ymin, ymax)

def drawObjectStartCostMap(featureBrowser, obj_esdc, l2_esdc, event_esdcs, 
                           annotation, beam_search, xmin, xmax, ymin, ymax, step):
    xend, yend = annotation.getGroundings(l2_esdc)[0].centroid2d
    ax, ay = annotation.agent.centroid2d
    ath_0 = annotation.agent.path.theta[0]
    print ax, ay, ath_0

    #agent move to pick up object

    costs = na.zeros((int((ymax-ymin)/step), int((xmax-xmin)/step)))
    annotations = []

    for i, x in enumerate(na.arange(xmin, xmax, step)):
        for j, y in enumerate(na.arange(ymin, ymax, step)):
            aX, aY = sf.math2d_step_along_line(tp([(ax, ay), (x, y)]), .1)
            aTh = ath_0 * na.ones(len(aX))

            X, Y = sf.math2d_step_along_line(tp([(x, y), (xend, yend)]), .1)

            Z = na.ones(len(X))
            th = na.zeros(len(X))
            timestamps = range(len(X))

            path = Path(timestamps, [X,Y,Z,th])
            
            new_annotation = annotation_copy(annotation)
            atimestamps = range(len(X)+len(aX))
            axs = na.append(aX, X)
            ays = na.append(aY, Y)
            azs = na.zeros(len(X) + len(aX))
            ath = na.append(aTh, th)
            new_annotation.agent.setPath(Path(atimestamps, [axs, ays, azs, ath]))
            

            obj = new_annotation.getGroundings(obj_esdc)[0]
            obj.setPath(path)
            assignPathGroundings(event_esdcs[0], new_annotation)
            cost, entries = beam_search.cf_obj.costEntry(event_esdcs, new_annotation)
            costs[j][i] = math.exp(-1.0*cost)
            annotations.append(((x,y), entries))

        print i
    featureBrowser.setCostImage(costs, annotations, xmin, xmax, ymin, ymax)


def drawObjectPathCostMap(featureBrowser, obj_esdc, event_esdcs, annotation, cf, xmin, xmax, ymin, ymax, step):
    xstart, ystart = annotation.getGroundings(obj_esdc)[0].centroid2d

    ax, ay = annotation.agent.centroid2d
    ath = annotation.agent.path.theta[0]
    print ax, ay, ath

    #agent move to pick up object
    aX, aY = sf.math2d_step_along_line(tp([(ax, ay), (xstart, ystart)]), .1)
    aTh = ath * na.ones(len(aX))

    costs = na.zeros((int((ymax-ymin)/step), int((xmax-xmin)/step)))
    annotations = []

    for i, x in enumerate(na.arange(xmin, xmax, step)):
        for j, y in enumerate(na.arange(ymin, ymax, step)):

            X, Y = sf.math2d_step_along_line(tp([(xstart, ystart), (x, y)]), .1)

            Z = na.ones(len(X))
            th = na.zeros(len(X))
            timestamps = range(len(X))

            path = Path(timestamps, [X,Y,Z,th])
            
            new_annotation = annotation_copy(annotation)
            atimestamps = range(len(X)+len(aX))
            axs = na.append(aX, X)
            ays = na.append(aY, Y)
            azs = na.zeros(len(X) + len(aX))
            ath = na.append(aTh, th)
            new_annotation.agent.path = Path(atimestamps, [axs, ays, azs, ath])

            obj = new_annotation.getGroundings(obj_esdc)[0]
            obj.path = path

            assignPathGroundings(event_esdcs[0], new_annotation)
           
            state, gggs = annotation_to_ggg_map(new_annotation)
            ggg = ggg_from_esdc(new_annotation.esdcs[0])
            factor = ggg.esdc_to_factor(event_esdcs[0])

            cost, entries = cf.compute_costs([factor], ggg, state_sequence=None)
            costs[j][i] = math.exp(-1.0*cost)
            annotations.append(((x,y), entries))
        print i
    featureBrowser.setCostImage(costs, annotations, xmin, xmax, ymin, ymax)

def drawAgentPathCostMap(featureBrowser, event_path_esdcs, annotation, cf, 
                         xmin, xmax, ymin, ymax, step):
    print "y", ymax, ymin
    xstart, ystart = (xmin + 0.5, (ymax + ymin) / 2.0)
    #xstart, ystart = 19.658, 14.900


    ath = 0
    print "start", xstart, ystart, ath

    costs = na.zeros((int((ymax-ymin)/step), int((xmax-xmin)/step)))
    state, gggs = annotation_to_ggg_map(annotation)
    esdc = event_path_esdcs[0]
    ggg = gggs[esdc]
    factor = ggg.esdc_to_factor(esdc)
    node = ggg.node_for_esdc(esdc)
    print "esdc", esdc
    print "node", node, node.__class__
    for i, x in enumerate(na.arange(xmin, xmax, step)):
        for j, y in enumerate(na.arange(ymin, ymax, step)):

            X, Y = sf.math2d_step_along_line(tp([(xstart, ystart), (x, y)]), .1)
            Z = na.ones(len(X))
            fig_xy = na.array([X, Y])
            
            Xst, Yst = fig_xy[:,:-1]
            Xend, Yend = fig_xy[:,1:]

            Theta = na.arctan2(Yend-Yst, Xend-Xst);
            Theta = list(Theta)
            Theta.append(Theta[-1])

            th = list(Theta)

            #th = ath*na.ones(len(X))
            timestamps = range(len(X))

            path = Path(timestamps, [X,Y,Z,th])
            pobj = PhysicalObject(Prism.from_point(X[0], Y[0], Z[0], Z[0] + 1),
                                  tags=("forklift",), path=path)
            ggg.set_evidence_for_node(node, [pobj])
            #new_annotation = annotation_copy(annotation)
            #new_annotation.agent = new_annotation.agent.withPath(path)

            #if esdc.type == "EVENT":
            #    assignPathGroundings(esdc, new_annotation)
            #else: #type is path
            #    new_annotation.setGrounding(esdc, new_annotation.agent.path)

            new_evidences = Evidences.copy(ggg.evidences)
            for phi in factor.nodes_with_type("phi"):
                new_evidences[phi.id] = True
            ggg = GGG.from_ggg_and_evidence(ggg, new_evidences)
#            print ggg.entry_for_factor(factor)
            cost, entries = cf.compute_costs([factor], ggg, state_sequence=None)
            costs[j][i] = math.exp(-1.0*cost)
            #annotations.append(((x,y), entries))

        print i
#        break
    print 'min/max', min(costs.flatten()), max(costs.flatten())
    featureBrowser.setCostImage(costs, xmin, xmax, ymin, ymax)
    return ggg


def go_to_the_truck_cost_path(cf):
    state, am = waverly_state_truck()
    cf.initialize_state(state)

    extractor = Extractor()
    esdcs = extractor.extractEsdcs("Go to the truck.")
    event_esdc = esdcs[0]
    path_esdc = event_esdc.l[0]
    truck_esdc = path_esdc.l[0]
    print "path", path_esdc
    annotation = initial_annotation(state, esdcs[0])

    truck = [o for o in state.objects if 'flatbed' in o.tags][0]

    annotation.setGrounding(truck_esdc, truck)
    featureBrowser = crfFeatureWeights.MainWindow()
    featureBrowser.show()
    ggg = drawAgentPathCostMap(featureBrowser, [path_esdc], annotation, cf, 
                               -15, 25, 15, 50, .5)
    factor = ggg.esdc_to_factor(path_esdc)
    featureBrowser.load(annotation.context, cf, factor)

def pick_up_the_pallet_cost_pickup(cf):
    state, am = waverly_state_truck()
    cf.initialize_state(state)

    extractor = Extractor()
    esdcs = extractor.extractEsdcs("Pick up the tire pallet.")
    event_esdc = esdcs[0]
    print 'event', event_esdc
#    pickup_esdc = event_esdc.r
#    print 'pickup', pickup_esdc
    pallet_esdc = event_esdc.l[0]
    print "pallet", pallet_esdc
    annotation = initial_annotation(state, esdcs[0])

    pallet = [o for o in state.objects if 'tire' in o.tags][0]

    annotation.setGrounding(pallet_esdc, pallet)
    featureBrowser = crfFeatureWeights.MainWindow()
    featureBrowser.show()
    ggg = drawObjectPathCostMap(featureBrowser, pallet_esdc, [event_esdc], 
                                annotation, cf, 
                               -20, 40, 15, 50, 1)
    factor = ggg.esdc_to_factor(event_esdc)
    featureBrowser.load(annotation.context, cf, factor)


def approach_the_truck_cost_path(cf):
    state, am = waverly_state_truck()
    cf.initialize_state(state)

    extractor = Extractor()
    esdcs = extractor.extractEsdcs("Approach the truck.")
    event_esdc = esdcs[0]
    truck_esdc = event_esdc.l[0]
    annotation = initial_annotation(state, esdcs[0])

    truck = [o for o in state.objects if 'flatbed' in o.tags][0]

    annotation.setGrounding(truck_esdc, truck)
    featureBrowser = crfFeatureWeights.MainWindow()
    featureBrowser.show()
    ggg = drawAgentPathCostMap(featureBrowser, [event_esdc], annotation, cf, 
                               -15, 25, 15, 50, 1)
    factor = ggg.esdc_to_factor(event_esdc)
    featureBrowser.load(annotation.context, cf, factor)




def on_the_truck_cost(cf):
    state, am = waverly_state_truck()
    print state.orientation
    #state.orientation = 3.14/6
    cf.initialize_state(state)
    
    extractor = Extractor()
    esdcs = extractor.extractEsdcs("next to the truck.")
    
    place_esdc = esdcs[0]
    place_esdc.type = "PLACE"
    truck_esdc = place_esdc.l[0]
    print "place", place_esdc, place_esdc.type
    print "truck", truck_esdc

    searcher = BeamSearch(cf)
    annotation = initial_annotation(state, esdcs[0])

    truck = [state.getGroundableById(o) for o in state.getObjectsSet() if 'flatbed' in state.getGroundableById(o).tags][0]

    annotation.setGrounding(truck_esdc, truck)
    annotation.setGrounding("sequence", [(state, None)])

    obj = prism_from_point(0, 0, truck.centroid3d[2]+.2, truck.centroid3d[2]+.5,
                           width=0.5)

    #axes = p.axes()
    featureBrowser = crfFeatureWeights.MainWindow()
    featureBrowser.show()
    axes = featureBrowser.axes
    for o in state.getObjectsSet():
        drawObject(axes, state.getGroundableById(o))

    drawPlaceCostMap(featureBrowser, obj, place_esdc, annotation, 
                     searcher, -5, 10, 25, 40, .2)
    #p.axes().set_aspect('equal')
    #p.show()
    state, gggs = annotation_to_ggg_map(annotation)
    ggg = gggs[place_esdc]
    #ggg = ggg_from_esdc(esdcs[0])
    factor = ggg.esdc_to_factor(place_esdc)
    print "factor", factor, factor.id
    print "cache", cf.factor_to_cost
    factor_to_cost = cf.factor_to_cost[factor] 

    print "cache", factor_to_cost
    featureBrowser.load(cf.lccrf, factor_to_cost)

def main():
    app = basewindow.makeApp()

    parser = OptionParser()

    parser.add_option("-t", "--model-filename",dest="model_fname", 
                      help="CRF Filename", metavar="FILE")
  
    (options, args) = parser.parse_args()
    print "loading model at:", options.model_fname

    cf = CostFnCrf.from_mallet(options.model_fname, guiMode=True)
    
    #on_the_truck_cost(cf)
#    go_to_the_truck_cost_path(cf)
    pick_up_the_pallet_cost_pickup(cf)
    #approach_the_truck_cost_path(cf)



    #put_the_tire_pallet_on_the_truck_cost(cf)
    #put_the_tire_pallet_on_the_truck_cost_start(cf)
    #go_to_the_truck_cost_go(cf)

    #go_to_the_truck_cost_full(cf)
    #put_the_tire_pallet_on_the_truck_cost_reflect(cf)
    #go_to_the_truck_cost(cf)
    #take_the_tire_pallet_to_the_truck_cost(cf)
    #left_pallet_cost(cf)
    #left_of_truck_pallet_cost(cf)
    #left_of_truck_pallet_cost(cf)
    #next_to_truck_pallet_cost(cf)
    #near_truck_pallet_cost(cf)


    app.exec_()


if __name__ == '__main__':
    main()
