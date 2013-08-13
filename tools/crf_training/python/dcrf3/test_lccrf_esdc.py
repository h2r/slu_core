import pickle_util
from sys import argv
from esdcs.dataStructures import ExtendedSdc, all_object_arguments
from confusion_matrix import ConfusionMatrix
from dcrf3.gui import resultsModel
from mallet.learners.crf_mallet import CRFMallet

def make_confusion_matrix(results):
    true_positives = [r for r in results if r.tp]
    true_negatives = [r for r in results if r.tn]
    false_positives = [r for r in results if r.fp]
    false_negatives = [r for r in results if r.fn]

    return ConfusionMatrix(len(true_positives), len(false_positives),
                           len(true_negatives), len(false_negatives))


        
def print_fraction_correct(presults):
    cm = make_confusion_matrix(presults)

    cm.print_all()


def fraction_correct(results):
    num_correct = sum(1 if result['correct'] else 0 for result in results)
    if len(results) == 0:
        return 0, 0
    else:
        return num_correct, float(num_correct) / len(results)

def test_lccrf(lcrf, test_obs):

    print '---------------------------------------------'
    results = []
    for i, obs in enumerate(test_obs):
        entry = resultsModel.Entry(i, lcrf, obs)
        results.append(entry)


    print_fraction_correct(results)

    print "******* esdc type"
    for esdcType in ExtendedSdc.types:
        presults = [r for r in results
                    if esdcType in [e.type for e in r.esdcs]]
        print esdcType, 
        print_fraction_correct(presults)

    print "******* node type"
    for esdcType in ExtendedSdc.types:
        presults = [r for r in results
                    if (r.node != None and 
                        r.node.grounding_type == esdcType)]
        print esdcType, 
        print_fraction_correct(presults)


    print "******* esdc type (events only; all object arguments)"
    presults = [r for r in results
                if (all("EVENT" == e.type for e in r.esdcs) and 
                    all_object_arguments(r.esdcs[0]))]
    print_fraction_correct(presults)


    print "******* esdc type (events only; not all object arguments)"
    presults = [r for r in results
                if (all("EVENT" == e.type for e in r.esdcs) and 
                    not all_object_arguments(r.esdcs[0]))]
    print_fraction_correct(presults)



    # print "******* esdc type (events only, non-empty)"
    # for esdcType in ExtendedSdc.types:
    #     presults = [r for r in results
    #                 if (all(esdcType == e.type for e in r.esdcs)
    #                     and len(r.obs.annotation.getGroundings(r.esdcs[0])) > 0 
    #                     and r.obs.ggg.annotation.getGroundings(r.esdcs[0])[0].path.length_seconds > 1)]

    #     print esdcType, 
    #     print_fraction_correct(presults)


    print "******* verbs"
    for verb in ["pick", "place", "move", "lift", "take ", "back", "turn ",
                 "proceed", "deposit", "put ", "go ", "prepare"]:
        
        presults = [r for r in results
                    if verb in " ".join(e.text.lower() for e in r.esdcs)]
        print verb,
        print_fraction_correct(presults)


    print "******* verbs (events only)"
    for verb in ["pick", "place", "move", "lift", "take ", "back", "turn ",
                 "proceed", "deposit", "put ", "go ", "prepare"]:
        presults = [r for r in results
                    if (all(e.type == "EVENT" for e in r.esdcs) and
                        verb in " ".join(e.text.lower() for e in r.esdcs))]
        print verb,
        print_fraction_correct(presults)


    print "******* objects and places"
    for relation in ["left", "right", " on ", "between", "next", "near", "front", " by ", " of ", "behind"]:
        presults = [r for r in results
                    if (relation in " ".join(e.text.lower() for e in r.esdcs) and
                        ("OBJECT" in [e.type for e in r.esdcs] or
                         "PLACE" in [e.type for e in r.esdcs]))]

        print relation,
        print_fraction_correct(presults)
    for relation in ["of", "on"]:
        presults = [r for r in results
                    if (all(relation == e.childText("r").lower() 
                            for e in r.esdcs) and
                        ("OBJECT" in [e.type for e in r.esdcs] or
                         "PLACE" in [e.type for e in r.esdcs]))]

        print "just", relation,
        print_fraction_correct(presults)

    print "******* paths"
    for relation in ["to", "across", "toward", "through", "along", "around", "left", "past"]:
        presults = [r for r in results
                    if (relation in " ".join(e.text.lower() for e in r.esdcs) and
                        "PATH" in [e.type for e in r.esdcs])]

        print relation,
        print_fraction_correct(presults)


    print "****** ons we are missing"
    for r in results:
        if (("OBJECT" in [e.type for e in r.esdcs] or
            "PLACE" in [e.type for e in r.esdcs]) and
            not r.correct and 
            " on " in " ".join(e.text.lower() for e in r.esdcs)):
            print ",".join(e.text.lower() for e in r.esdcs)

    print "****** to we are missing"
    for r in results:
        if (("OBJECT" in [e.type for e in r.esdcs] or
            "PLACE" in [e.type for e in r.esdcs]) and
            not r.correct and 
            " to " in " ".join(e.text.lower() for e in r.esdcs)):
            print ",".join(e.text.lower() for e in r.esdcs)


    print "****** pick we are missing"
    for r in results:
        if ("EVENT" in [e.type for e in r.esdcs] and 
            not r.correct and 
            "pick " in " ".join(e.text.lower() for e in r.esdcs)):
            print ",".join(e.text.lower() for e in r.esdcs)



    print "****** go we are missing"
    for r in results:
        if ("EVENT" in [e.type for e in r.esdcs] and
            r.correct and 
            "go " in " ".join(e.text.lower() for e in r.esdcs)):
            print ",".join(e.text.lower() for e in r.esdcs)




            
    
    print "****** objects we are missing"
    for r in results:
        if "OBJECT" in [e.type for e in r.esdcs] and not r.correct:
            print ",".join(e.text.lower() for e in r.esdcs)

    print "****** events we are missing"
    for r in results:
        if "EVENT" in [e.type for e in r.esdcs] and not r.correct:
            print ",".join(e.text.lower() for e in r.esdcs)

    print "****** fridges"
    presults = []
    for r in results:
        if "OBJECT" in [e.type for e in r.esdcs]:
            if r.obs.annotation != None:
                groundings = r.obs.annotation.getGroundings(r.esdcs[0])
                
                if (len(groundings) > 0 and hasattr(groundings[0], "tags") and 
                    "refrigerator" in groundings[0].tags):
                    presults.append(r)
                    if not r.correct:
                        print r.correct, r.esdcs[0].text
    print_fraction_correct(presults)


            
def main():
    dataset = pickle_util.load(argv[1])
    test_lccrf(CRFMallet.load(argv[2]), dataset.observations)

if __name__=="__main__":
    main()
    
