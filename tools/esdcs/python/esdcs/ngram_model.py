# Import the corpus and functions used from nltk library  
from nltk.probability import LidstoneProbDist  
import nltk
import argparse
import math
import ngram

# Tokens contains the words for Genesis and Reuters Trade  
from esdcs.esdcIo import annotationIo

class NgramModel:

    @staticmethod
    def from_corpus(corpus, n):
        tokens = []
        for annotation in corpus:
            tokens.extend(annotation.entireText.split(" "))
        return NgramModel(tokens, n)

    def __init__(self, tokens, n):

        self.n = n
        self.tokens = tokens

        #tokens = list(genesis.words('english-kjv.txt'))  
        #tbokens.extend(list(reuters.words(categories = 'trade')))  

        # estimator for smoothing the N-gram model  
        estimator = lambda fdist, bins: LidstoneProbDist(fdist, 0.2)  

        self.models = [ngram.NgramModel(n + 1, tokens,estimator) for n in range(self.n)]


    def prob(self, word, context):
        new_context = context[-(self.n - 1):]

        if len(new_context) == 0:
            model = self.models[0]
        else:
            model_idx = len(new_context)
            model = self.models[model_idx]



        prob = model.prob(word, new_context)
        assert 0 <= prob <= 1, (prob, word, context, new_context)
        return prob

    def log_probability(self, word, context):
        return -math.log(self.prob(word, context))


    def generate(self, number_of_words):
        return self.models[-1].generate(number_of_words)

    def sentence_probability(self, text):
        return math.exp(-self.sentence_log_probability(text))

    def sentence_log_probability(self, text):

        """ Evaluate the total probability of a text with respect to
        the model.  This is the sum of the log probability of each
        word in the message.""" 
        e = 0.0 
        for i in range(0, len(text)):
            start_context = max(0, i - self.n)
            end_context = i

            context = tuple(text[start_context:end_context]) 

            token = text[i] 
            lp = self.prob(token, context)
            e += lp

        return e 


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-filename",
                        dest="corpus_fnames", action="append")
    args = parser.parse_args()
    corpus = annotationIo.load_all(args.corpus_fnames)
    model = NgramModel.from_corpus(corpus, n=3)
    
    # Apply the language model to generate 50 words in sequence  
    text_words = model.generate(50)  

    # Concatenate all words generated in a string separating them by a space.  
    text = ' '.join([word for word in text_words])  

    # print the text  
    print text  
    print model.prob("table", [])
    print model.prob("table", ["the", "white"])
    print model.prob("leg", ["the", "white"])
    print model.prob("one", ["the", "white"])

    print "probability", model.sentence_probability("Pick up the white leg".split())
    print "probability", model.sentence_probability("Put the white leg near me".split())
    print "probability", model.sentence_probability("Screw in the white leg".split())
    print "probability", model.sentence_probability("Screw up the white leg".split())
    
if __name__ == "__main__":
    main()
