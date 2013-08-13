from esdcs.extractor import lccrfRerankingExtractor
from esdcs.extractor import stanfordParserExtractor




def annotatedEsdcExtractor(annotation):
    return annotation.esdcs


def makeAutomaticEsdcExtractorFunc(extractor):
    def resultFunc(annotation):
        return extractor.extractEsdcs(annotation.entireText)

    return resultFunc


def make_extractor(esdc_extractor_name, model_name=None):
    """
    Creates a function to get extractors from an annotation. Useful
    to create an extractor by name from command line arguments.
    """
    if esdc_extractor_name == "lccrfRerankingExtractor":
        extractor = lccrfRerankingExtractor.Extractor(model_name)
    elif esdc_extractor_name == "stanfordParserExtractor":
        extractor = stanfordParserExtractor.Extractor()
    else:
        raise ValueError("Unexpected value for esdc_extractor: " +
                         `esdc_extractor_name`)
    return extractor


def make_extractor_func(esdc_extractor_name, model_name=None):
    """
    Creates a function to get extractors from an annotation. Useful
    to create an extractor by name from command line arguments.
    """
    if esdc_extractor_name == "annotated":
        extractor_func = annotatedEsdcExtractor
    elif esdc_extractor_name == "ETreeExtractor":
        import etree.extractor
        return etree.extractor.extractEsdcs
    elif esdc_extractor_name == "ChunkerExtractor":
        import esdc_chunker.chunker
        return esdc_chunker.chunker.extractEsdcs
    else:
        extractor = make_extractor(esdc_extractor_name, model_name)
        extractor_func = makeAutomaticEsdcExtractorFunc(extractor)

    return extractor_func
