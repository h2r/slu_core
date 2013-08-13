from nltk.tokenize.punkt import PunktSentenceTokenizer
from standoff import TextStandoff


class SentenceTokenizer:
    def __init__(self):
        self.tokenizer = PunktSentenceTokenizer()
        
    def tokenize(self, string):
        instructions = string
        sentences = self.tokenizer.tokenize(instructions)
        standoffs = []
        lastStart = 0
        for sentence in sentences:
            startIdx = instructions.index(sentence, lastStart)
            endIdx = startIdx + len(sentence)
            standoffs.append(TextStandoff(string, (startIdx, endIdx)))
            lastStart = endIdx
        for s1 in standoffs:
            for s2 in standoffs:
                assert s1 == s2 or not s1.overlaps(s2)
        return standoffs
                           
            

    
