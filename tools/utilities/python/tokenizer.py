from nltk.tokenize.punkt import PunktWordTokenizer
from standoff import TextStandoff, correctStandoff
from sentenceTokenizer import SentenceTokenizer
class IndexedTokenizer:
    
    def __init__(self, nltkTokenizer=PunktWordTokenizer()):
        self.nltkTokenizer = nltkTokenizer
        self.sentenceTokenizer = SentenceTokenizer()
    def tokenize(self, string):
        tokens = []
        for sentence in self.sentenceTokenizer.tokenize(string):
            word_tokens = self.word_tokenize(sentence.text)
            for w in word_tokens:
                correctStandoff(sentence, w)
            tokens.extend(word_tokens)
        return tokens
                
                              
                

    def word_tokenize(self, string):
        """
        Tokenize a string, returning a tuple. The first element is a
        list of starting locations for the tokens and the second
        element is a list of tokens.
        """
        tokens = self.nltkTokenizer.tokenize(string)
        indexes = []
        startIdx = 0
        for token in tokens:
            idx = string.index(token, startIdx)
            indexes.append(idx)
            startIdx = idx + len(token)
        if len(tokens) > 0:
            lastToken = tokens[-1]
            if len(lastToken) > 1 and lastToken[-1] in ('?','.','!'):
                lastCharacter = lastToken[-1]
                tokens[-1] = lastToken[0:-1]
                tokens.append(lastCharacter)
                indexes.append(indexes[-1] + len(lastToken) - 1)

        return [TextStandoff(string, (i, i + len(token))) 
                for i, token in zip(indexes, tokens)]

