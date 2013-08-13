from esdcs.extractor.stanfordParserExtractor import Extractor as StanfordExtractor
from g3.esdcs_to_ggg import ggg_from_esdc_group
from yn_dialog.graph import YNGGG
from coreference.merge_coreferences import renumber_ggg_ids, merge_gggs
from dialog.question_answer_corpus import QACorpus


qa_corpus = QACorpus([])

sentence = 'Pick up the tire pallet near the truck.'
# sentence = 'Turn away from the truck and move forward'
# sentence = "I went to the store."
# sentence = 'Raise the forks, turn right, and proceed forward for a few seconds.'

stanford_extractor = StanfordExtractor()
stanford_esdcs = stanford_extractor.extractEsdcs(sentence)
ggg = ggg_from_esdc_group(stanford_esdcs)
ggg, max_id = renumber_ggg_ids(ggg, 0)

target_node_id = '4'
target_node = ggg.node_from_id(target_node_id)
target_factors = ggg.factors_for_node(target_node, 'top')
target_esdc = ggg.factor_to_esdc(target_factors[0])
target_text = target_esdc.text

command_text = ggg.entireText
oid = '??'
question_text = qa_corpus.generate_base_question_text(target_text) + " " + oid + "?"
qa_text = question_text + " " + "Yes."
yn_ggg = YNGGG.from_dialog(ggg.entireText, qa_text, True)
yn_ggg, max_id = renumber_ggg_ids(yn_ggg, max_id)


entireText = ' '.join((command_text, qa_text))
ggg.entireText = entireText
for esdc in ggg.flattened_esdcs:
    esdc.entireText = entireText
    for fieldName, children in esdc.fields.iteritems():
        for child in children:
            child.entireText = entireText

merged_ggg = merge_gggs(yn_ggg, ggg, (target_factors[0], yn_ggg.factors[0]))
merged_ggg.to_file('dot_graph.dot', use_edge_labels=False)
