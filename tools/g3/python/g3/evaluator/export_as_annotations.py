from optparse import OptionParser
from g3.evaluator.evaluateCorpus import ResultsFile
from g3.evaluator.evaluate_object_nodes import compute_node_results
from esdcs.esdcIo.annotationIo import Annotation
from esdcs.esdcIo import annotationIo 
from esdcs.dataStructures import breadthFirstTraverse
from g3.evaluator.gui import resultsModel


def make_annotation_for_result(old_annotation, result):
    a = Annotation(old_annotation.id, old_annotation.esdcs, 
                   agent=old_annotation.agent, 
                   context=old_annotation.context)
    node_results = [nr for nr in compute_node_results([result]) if not nr.is_null_node]
    for node_result in node_results:
        a.setGrounding(node_result.node_esdc, node_result.inferred_pobj)
        a.setGroundingIsCorrect(node_result.node_esdc, node_result.correct)

    for node_result in node_results:
        def callback(esdc):
            if not a.hasGroundings(esdc):
                a.setGrounding(esdc, node_result.inferred_pobj)
                a.setGroundingIsCorrect(esdc, node_result.correct)
                
        breadthFirstTraverse(node_result.node_esdc, callback)
                               
    
    return [a]
    


def main():
    parser = OptionParser()
    parser.add_option("--result-fname", dest="result_fname")
    parser.add_option("--state-type", dest="state_type")
    (options, args) = parser.parse_args()
    results = ResultsFile(options.result_fname)
    entries = resultsModel.Entry.entries_from_results_file(results)

    annotation_id_to_entries = {}

    for entry in entries:
        annotation_id_to_entries.setdefault(entry.annotation.id, [])
        annotation_id_to_entries[entry.annotation.id].append(entry)
        

    new_corpus = []
    
    for i, (aid, entries) in enumerate(annotation_id_to_entries.iteritems()):
        annotation = entries[0].annotation

        for entry in entries:
            assert entry.annotation.id == annotation.id
            new_corpus.extend(make_annotation_for_result(annotation, 
                                                         entry.best_result_as_entry()))
        if i > 10:
            break
    annotationIo.save(new_corpus, "negative_from_inference.yaml")
            
    
    print "entries", len(entries)

if __name__ == "__main__":
    main()
