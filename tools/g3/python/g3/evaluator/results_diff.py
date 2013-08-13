from g3.evaluator.evaluateCorpus import ResultsFile
from optparse import OptionParser
import cPickle
import numpy as na

def peq(o1, o2):
    s1 = cPickle.dumps(o1)
    s2 = cPickle.dumps(o2)
#    print "s1", s1
#    print "s2", s2
    return s1 == s2
def deq(o1, o2, already_seen_ids=None):
    print "deq testing", o1.__class__
    if already_seen_ids == None:
        already_seen_ids = set()
    else:
        if id(o1) in already_seen_ids or id(o2) in already_seen_ids:
            return False
    already_seen_ids = set(already_seen_ids)
    already_seen_ids.add(id(o1))
    already_seen_ids.add(id(o2))
                                   
    if isinstance(o1, str):
        print o1, o2, o1 == o2
        assert o1 == o2
    elif isinstance(o1, float) and na.isnan(o1) and na.isnan(o2):
        print "nan"
    elif hasattr(o1, "__dict__"):
        print "attr"
        for key1, value1 in o1.__dict__.iteritems():
            print "testing", o1.__class__, key1,
            value2 = o2.__dict__[key1]
            deq(value1, value2, already_seen_ids)
    elif isinstance(o1, dict):
        print "dict"
        for k1, v1 in o1.iteritems():
            v2 = o2[k1]
            deq(v1, v2, already_seen_ids)
    elif hasattr(o1, "__len__"):
        print "list"
        print "len", len(o1), len(o2), len(o1) == len(o2)
        for v1, v2 in zip(o1, o2):
            deq(v1, v2, already_seen_ids)
    else:
        print (o1, o2), o1 == o2 
        assert o1 == o2




def main():
    parser = OptionParser()
    parser.add_option("--result1-fname", dest="result1_fname")
    parser.add_option("--result2-fname", dest="result2_fname")


    (options, args) = parser.parse_args()

    results1 = ResultsFile(options.result1_fname)
    results2 = ResultsFile(options.result2_fname)

    assert len(results1) == len(results2), (len(results1), len(results2))


               
    for (glist1, rlist1), (glist2, rlist2) in zip(results1.results, results2.results):

        
        #deq(glist1, glist2)
        assert peq(glist1, glist2)
        assert peq(rlist1, rlist2)
        
        continue
        assert len(rlist1) == len(rlist2)
        assert len(glist1) == len(glist2)
        print "ASSSIGNMENT", rlist1[0].annotation.id
        for ggg1, ggg2 in zip(glist1, glist2):
            for n in ggg1.nodes:
                n.graph = None
            for n in ggg2.nodes:
                n.graph = None
            print "testing nodes"
            for node1, node2 in zip(ggg1.nodes, ggg2.nodes):
                deq(node1, node2)
            print "done testing nodes"
            print "testing node_id_to_nodes"
            for id1, node1 in ggg1._graph.node_id_to_node.iteritems():
                node2 = ggg2._graph.node_id_to_node[id1]
                node1.graph = None
                node2.graph = None
            print "done testing node_id_to_nodes"
            print "testing ggg1, ggg2"
            deq(ggg1, ggg2)
            print "done testing ggg1, ggg2"
        #assert peq(rlist1, rlist2)

        for r1, r2 in zip(rlist1, rlist2):
            deq(r1, r2)
if __name__ == "__main__":
    main()
