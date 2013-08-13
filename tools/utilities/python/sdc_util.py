from routeDirectionCorpusReader import TextStandoff, Annotation
import crfEntityExtractor

class direction_parser_sdc:
    def __init__(self):
        self.extractor = crfEntityExtractor.SdcExtractor()

    def extract_SDCs(self, mystr):
        return self.extractor.chunk(mystr)


def sdc_hmap_to_sdc_standoff(sdc_hmap):
    
    sent = sdc_hmap["figure"]+" "+sdc_hmap["verb"]+" "+sdc_hmap["sr"]+" "+sdc_hmap["landmark"]
    l1 = len(sdc_hmap["figure"])
    l2 = len(sdc_hmap["verb"])
    l3 = len(sdc_hmap["sr"])
    l4 = len(sdc_hmap["landmark"])
    
    t1 = TextStandoff(sent, (0,l1))
    t2 = TextStandoff(sent, (l1+1,l1+1+l2))
    t3 = TextStandoff(sent, (l1+l2+2,l1+l2+2+l3))
    t4 = TextStandoff(sent, (l1+l2+l3+3,l1+l2+l3+3+l4))
    
    return Annotation(figure=t1, verb=t2, spatialRelation=t3, landmark=t4)
