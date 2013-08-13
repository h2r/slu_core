import unittest
import sentenceTokenizer

class SentenceTokenizerTestCase(unittest.TestCase):
    def testSentenceTokenizer(self):
        tokenizer = sentenceTokenizer.SentenceTokenizer()
        standoffs = tokenizer.tokenize("""With your back to the windows, walk straight through the door near the elevators.  Continue
    to walk straight, going through one door until you come to an intersection just
    past a whiteboard.  Turn left, turn right, and enter the second door on your right
    (sign says "Administrative Assistant").""")

        self.assertEqual(len(standoffs), 3)
        self.assertEqual(standoffs[0].text,
                         "With your back to the windows, walk straight through the door near the elevators.")
    def testRepeatedSentences(self):
        tokenizer = sentenceTokenizer.SentenceTokenizer()
        string = "Turn right.  Turn right."
        standoffs = tokenizer.tokenize(string)
        print standoffs
        sentences = [string[standoff.range[0]:standoff.range[1]] for standoff in standoffs]
        self.assertEqual(sentences[0], "Turn right.")
        self.assertEqual(sentences[1], "Turn right.")

        
        
