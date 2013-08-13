from tokenizer import IndexedTokenizer
import collections
from sentenceTokenizer import SentenceTokenizer
                   
def pos_histograms(discourses, 
                   pos_tagger,
                   tag_groups={"Verbs":["VBZ", "VB"],
                               "Nouns":["NN", "NNS"],
                               "Prepositions":["IN", "TO", "UNTIL", "OF"],
                               "Adjectives":["JJ"],
                               }):

    stokenizer = SentenceTokenizer()
    tokenizer = IndexedTokenizer()
    tag_groups_to_words = collections.defaultdict(lambda : list())
    

    for discourse in discourses:
        for sentence_standoff in stokenizer.tokenize(discourse):
            tokens = tokenizer.tokenize(sentence_standoff.text)
            for key_tag, tag_group in tag_groups.iteritems():
                tags = pos_tagger.tag([t.text.lower() for t in tokens])
                for token, tag in tags:
                    if tag in tag_group:
                        tag_groups_to_words[key_tag].append(token)
                    tag_groups_to_words["all"].append(token)

    print "dumping counts"
    for pos, words in tag_groups_to_words.iteritems():
        print len(words), pos
        print len(set(words)), "unique", pos
        w_to_counts = collections.defaultdict(lambda : 0)
        for w in words:
            w_to_counts[w] += 1

        cnt_target = 10
        frequent_words = [(w, cnt) for w, cnt in w_to_counts.iteritems() 
                          if cnt > cnt_target]
        print len(frequent_words)
        print "if appeared more than %d times" % cnt_target
        print frequent_words

    print "done"
    return tag_groups_to_words

        
