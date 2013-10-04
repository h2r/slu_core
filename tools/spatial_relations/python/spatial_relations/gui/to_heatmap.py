from spatial_features.groundings import PhysicalObject, Prism, Path
from optparse import OptionParser
import spatial_features_cxx as sf
from esdcs.gui import drawUtils
from esdcs import esdcIo
from esdcs.context import Context
import pylab as mpl
from numpy import transpose as tp
import numpy as na
from g3.esdcs_to_ggg import gggs_from_esdc_group
from g3.graph import Evidences, GGG
from g3.cost_functions.cost_function_crf import CostFnCrf

def prism_from_point(x,y,z1,z2):
     return Prism.from_points_xy([(x-1, x+1, x+1, x-1), (y-1, y-1, y+1, y+1)], z1, z2)

def initialize_ggg_context(state, ggg, state_object = None):
    """
    Set the context and agent for a ggg.
    """
    ax, ay = state.getPosition()
    agent_prism  = prism_from_point(ax, ay, 0, 1)
    agent_object = PhysicalObject(agent_prism, [], 
                                  Path.from_xyztheta([1], [[ax], [ay], [0], [state.orientation]]), 
                                  lcmId=state.getAgentId())
    context = state.to_context()
    context.agent = agent_object
    ggg.context = context
    return ggg


def path_probabilities(cf,
                       path_factor, path_node, ggg,
                       xmin, xmax, ymin, ymax, step):
    """
    Compute probabilities of endpoints in the given range of a 
    top-level agent path given a path node and an associated factor
    in a ggg, a weights vector, and a cost function.
    """

    xstart, ystart = (xmin + 0.5, (ymax + ymin) / 2.0)

    ath = 0


    probs = na.zeros((int((ymax-ymin)/step), int((xmax-xmin)/step)))
    prob_idx_to_xy = {}
    for i, x in enumerate(na.arange(xmin, xmax, step)):
        for j, y in enumerate(na.arange(ymin, ymax, step)):
            
            X, Y = sf.math2d_step_along_line(na.transpose([(xstart, ystart), 
                                                           (x, y)]), .1)
            Z = na.ones(len(X))
            fig_xy = na.array([X, Y])

            Xst, Yst = fig_xy[:,:-1]
            Xend, Yend = fig_xy[:,1:]

            Theta = na.arctan2(Yend-Yst, Xend-Xst);
            Theta = list(Theta)
            Theta.append(Theta[-1])

            th = list(Theta)

            timestamps = range(len(X))

            path = Path.from_xyztheta(timestamps, [X,Y,Z,th])
            pobj = PhysicalObject(Prism.from_point(X[0], Y[0], Z[0], Z[0] + 1),
                                  tags=("forklift",), path=path)

            ggg.set_evidence_for_node(path_node, [pobj])
            new_evidences = Evidences.copy(ggg.evidences)
            for phi in path_factor.nodes_with_type("phi"):
                new_evidences[phi.id] = True
            ggg = GGG.from_ggg_and_evidence(ggg, new_evidences)
            
            print "**** computing entry"
            ce = cf.compute_factor_cost_entry(path_factor, ggg, None)
            print "**** done computing entry", ce.probability
            probs[j][i] = ce.probability

            prob_idx_to_xy[(j, i)] = (x, y)
            #break
        print i
        #break

    print 'min/max', min(probs.flatten()), max(probs.flatten())
    print "max idx", na.argmax(probs)
    max_idx = na.argmax(probs)
    max_tuple = na.unravel_index(max_idx, probs.shape)
    print "max x,y", prob_idx_to_xy[max_tuple]
    return (probs, xstart, ystart)


def draw(probs, xmin, xmax, ymin, ymax, 
         xstart, ystart, agent, landmark, output_fname = None, title=None):
    figure = mpl.figure()
    axes = figure.gca()

    axes.imshow(probs, origin="lower", extent=(xmin, xmax, ymin, ymax),
                       cmap=mpl.cm.jet)
    print" drawing", agent, agent.centroid2d
    drawUtils.drawGrounding(axes, agent)
    drawUtils.drawGrounding(axes, landmark)

    if title:
        figure.suptitle( title )

    axes.axis([xmin, xmax, ymin, ymax])
    #axes.get_xaxis().set_visible(False)
    #axes.get_yaxis().set_visible(False)
    figure.canvas.draw()
    if output_fname is not None:
        mpl.savefig( output_fname )
    else:
        mpl.show()


def generate_go_to_heat_map(esdcs, cf, output_fname=None, title=None):
    path_esdc = esdcs[0]
    landmark_esdc = path_esdc.l[0]

    agent = PhysicalObject(Prism.from_points_xy(tp([(-1, -1), (1, -1), (1, 1), (-1, 1)]),
                                                    0, 2),
                               tags=("robot",), 
                               lcmId=-1)

    landmark = PhysicalObject(Prism.from_points_xy(tp([(9, -1), (10, -1), (10, 1), (9, 1)]), 0, 2), tags=("truck",), lcmId=3)
    
    context = Context.from_groundings([agent, landmark])

    

    print 'path', path_esdc

    gggs = gggs_from_esdc_group(esdcs)
    ggg = gggs[0]
    context.agent = agent
    ggg.context = context

    path_factor = ggg.esdc_to_factor(path_esdc)
    path_node = ggg.node_for_esdc(path_esdc)
    landmark_node = ggg.node_for_esdc(landmark_esdc)
    ggg.set_evidence_for_node(landmark_node, [landmark])



    probs, xstart, ystart = path_probabilities(cf, 
                                               path_factor, path_node, ggg,
                                               -5, 15, -10, 10, 1)
    print "starting draw"
    draw(probs, -5, 15, -10, 10, xstart, ystart, 
         agent, landmark, output_fname=output_fname, title=title)


def main():
    parser = OptionParser()
    parser.add_option("--model-filename", dest="model_fname")
    (options, args) = parser.parse_args()

    crf_fname = options.model_fname
    cf = CostFnCrf.from_mallet(crf_fname)


    esdcs = esdcIo.parse("""
- 'to the truck'
- - PATH:
      r:  to
      l:  the truck
""")

    generate_go_to_heat_map(esdcs, cf)



if __name__ == "__main__":
    main()
