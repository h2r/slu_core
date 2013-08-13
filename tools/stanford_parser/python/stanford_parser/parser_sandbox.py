from stanford_parser.parser import Parser, startJvm
from esdcs.extractor.stanfordParserExtractor import Extractor
from g3.esdcs_to_ggg import ggg_from_esdc_group
import nltk


startJvm()
parser = Parser()
sentence = 'Pick up the tire pallet.'

tokens, parses = parser.parseTopN(sentence, 5)

# for p in parses:
#     score = p[0]
#     tree = p[1]
#     print tree
#     nltk.tree.Tree.parse(str(tree)).draw()

extractor = Extractor()
results = extractor.extractTopNEsdcsFromSentence(sentence, 5)

for result in results:
    print result

best_esdcs = results[0]

ggg = ggg_from_esdc_group(best_esdcs)
print ggg



