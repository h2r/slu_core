from esdcs.esdcIo import annotationIo, toYaml, fromYaml
from esdcs.dataStructures import ExtendedSdc, ExtendedSdcGroup
from standoff import TextStandoff
from numpy import transpose as tp
from esdcs.context import Context
from esdcs.groundings import PhysicalObject, Prism, Path
from math import pi

def log_to_context(fname):
    # timestamps in micro
    pobj1 = PhysicalObject(Prism(tp([(0, 0), (1, 0), (1, 1), (0, 1)]),
                                 zStart=0, zEnd=1),
                           tags=("block", "red"),
                           path=Path(timestamps=[0, 1, 2, 3, 4, 5],
                                     points_xyztheta=tp([(0, 0, 0, 0), 
                                                         (1, 1, 1, 0), 
                                                         (2, 2, 2, 0),
                                                         (3, 3, 3, 0),
                                                         (4, 4, 4, 0),
                                                         (5, 5, 5, pi/4),
                                                         ])),
                           lcmId=0)
    # [(x,y)
    agent = PhysicalObject(Prism(tp([(1, 1), (2, 1), (2, 2), (1, 2)]),
                                 zStart=0, zEnd=2),
                           tags=("robot",),
                           lcmId=-100)

    return Context([pobj1, agent], [])

def main():
    corpus = []
    fake_turk_commands = [("Pick up the tire pallet", "fake_log_fname.bag")]

    for i, (command, bag_fname) in enumerate(fake_turk_commands):
        standoff = TextStandoff(command, (0, len(command)))
        esdc = ExtendedSdc("EVENT", entireText=command, r=standoff)
        esdcs = fromYaml(*toYaml(ExtendedSdcGroup([esdc])))
        annotation_id = "%s_%d" % (bag_fname, i)

        annotation = annotationIo.Annotation(annotation_id, 
                                             esdcs,
                                             context=log_to_context(bag_fname))
        corpus.append(annotation)
    annotationIo.save(corpus, "test.yaml")
        
        
        


if __name__=="__main__":
    main()

    
