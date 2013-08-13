import unittest
from tokenizer import IndexedTokenizer
from nltk.tokenize import PunktWordTokenizer, TreebankWordTokenizer
from sentenceTokenizer import SentenceTokenizer

class AnnotationTestCase(unittest.TestCase):
    def testPunktTokenizer(self):
        tokenizer = IndexedTokenizer(PunktWordTokenizer())
        string = " Facing the long wall in front of you, your destination will be the first door to your left (36-880)."
        tokens = tokenizer.tokenize(string)
        self.assertEqual([t.text for t in tokens],
                         ['Facing', 'the', 'long', 'wall', 'in', 'front', 'of', 'you', ',', 'your', 'destination', 'will', 'be', 'the', 'first', 'door', 'to', 'your', 'left', '(', '36-880', ')', '.'])

        for i, token in enumerate(tokens):
            self.assertEqual(string[tokens[i].start:tokens[i].end], token.text)

        


    def testPunktTokenizerContraction(self):
        tokenizer = IndexedTokenizer(PunktWordTokenizer())
        string = " You'll see a large white question mark."
        tokens = tokenizer.tokenize(string)
        self.assertEqual([t.text for t in tokens],
                         ['You', "'ll", 'see', 'a', 'large', 'white', 'question', 'mark', '.'])

        for i, token in enumerate(tokens):
            self.assertEqual(string[tokens[i].start:tokens[i].end], token.text)

        

    def testPunktTokenizerNiceView(self):
        tokenizer = IndexedTokenizer(PunktWordTokenizer())
        string = "you should have  a    nice   view ."
        tokens = tokenizer.tokenize(string)
        self.assertEqual([t.text for t in tokens],
                         ['you', "should", 'have', 'a', 'nice', 'view', '.'])
        self.assertEqual([t.start for t in tokens],
                         [0,      4,       11,     17,   22,     29,     34])

        for i, token in enumerate(tokens):
            self.assertEqual(string[tokens[i].start:tokens[i].end], token.text)

        



    def testTreebankTokenizer(self):
        tokenizer = IndexedTokenizer(TreebankWordTokenizer())
        string = " Facing the long wall in front of you, your destination will be the first door to your left (36-880)."
        tokens = tokenizer.tokenize(string)
        self.assertEqual([t.text for t in tokens],
                         ['Facing', 'the', 'long', 'wall', 'in', 'front', 'of', 'you', ',', 'your', 'destination', 'will', 'be', 'the', 'first', 'door', 'to', 'your', 'left', '(', '36-880', ')', '.'])

        for i, token in enumerate(tokens):
            self.assertEqual(string[tokens[i].start:tokens[i].end], token.text)

        


    def testEmpty(self):
        tokenizer = IndexedTokenizer()
        tokens = tokenizer.tokenize("  ")
        self.assertEqual(len(tokens), 0)
        


    def testMultipleSentences(self):
        tokenizer = IndexedTokenizer()
        sentences = """With your back to the windows, walk straight through the door near the elevators.  Continue
    to walk straight, going through one door until you come to an intersection just
    past a whiteboard.  Turn left, turn right, and enter the second door on your right
    (sign says "Administrative Assistant").  """
        tokens = tokenizer.tokenize(sentences)
        for token in tokens:
            print str(token)

        self.assertEqual(tokens[14].text, "elevators")
        self.assertEqual(tokens[15].text, ".")
        
