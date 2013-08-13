import jpype
from standoff import TextStandoff
import os

class ParserError(Exception):
    def __init__(self, *args, **margs):
        Exception.__init__(self, *args,**margs)


def standoffFromToken(txt, token):
    return TextStandoff(txt, (token.beginPosition(), token.endPosition()))


class Dependencies:
    def __init__(self, sentence, tokens, posTags, dependencies, score):
        self.sentence = sentence

        self.posTags = posTags        
        
        self.tokens = tokens

        self.tokensToPosTags = dict(zip(self.tokens, self.posTags))

        self.dependencies = dependencies

        self.score = score
        
        self.govToDeps = {}
        self.depToGov = {}
        self.constituentsToRelation = {}

        # there is a bug where sometimes there is a self dependency.
        self.dependencies = [(relation, gov, dep) for relation, gov, dep in self.dependencies
                             if gov != dep]


        for relation, gov, dep in self.dependencies:
            
            self.govToDeps.setdefault(gov, [])
            self.govToDeps[gov].append(dep)
            if dep in self.depToGov and False:
                print "text",(dep.text, [(key.text, value.text)
                                         for key, value in self.depToGov.iteritems()])
                print "this dep", gov, relation, dep
                print "dep to gov"
                for dep, gov in self.depToGov.iteritems():
                    print dep, gov
                print "dependencies"
                for relation, gov, dep in self.dependencies:
                    print gov, relation, dep
                raise ValueError("Dep should not be in depToGov already.")
            self.depToGov[dep] = gov
            self.constituentsToRelation[(gov,dep)] = relation
            
        self.checkRep()

    def tagForTokenStandoff(self, tokenStandoff):
        return self.tokensToPosTags[tokenStandoff]
        
        
    def checkRep(self):
        assert len(self.posTags) == len(self.posTags)        
        for t in self.tokens:
            assert t.entireText == self.sentence

    def __getitem__(self, item):
        return self.dependencies[item]


    def govForDep(self, dep):
        return self.depToGov[dep]
    def depsForGov(self, gov):
        return self.govToDeps[gov]

    def relForConstituents(self, gov, dep):
        return self.constituentsToRelation((gov, dep))
    
    def __str__(self):
        result = ""
        result += "sentence=" + repr(self.sentence) + "\n"
        for relation, gov, dep in self.dependencies:
            result += relation + "(" + gov.text + ", " + dep.text + ")\n"
        return result


    def __repr__(self):
        return "Dependencies(%s, %s, %s, %s, %s)" % tuple(repr(x) for x in
                                                          [self.sentence,
                                                           self.tokens,
                                                           self.posTags,
                                                           self.dependencies,
                                                           self.score])

    

stanford_parser_home = None
stanford_parser_data_home = None
def classpath():
    global stanford_parser_home
    global stanford_parser_data_home
    stanford_parser_home = os.environ["JAVA_LIB"]
    stanford_parser_data_home = os.environ["DATA_HOME"]+"stanford-parser/"

from jvm import startJvm
    
classpath()


    

#def classpath():
#    import os
#    #os.environ.setdefault("STANFORD_PARSER_HOME",
#    #                      "3rdParty/stanford-parser/stanford-parser-2010-11-30")
#
#    return "%s/stanford-parser.jar" % (stanford_parser_home)

#startJvm() # one jvm per python instance.
parser = None

def getParser():
    """
    Make it a singleton. The JVM apparently doesn't like more than one
    instance.  It crashed with a NullPointerException.
    """
    global parser
    if parser == None:
        parser = Parser()
    return parser

class Parser:

    def __init__(self, pcfg_model_fname=None):
        if pcfg_model_fname == None:
            self.pcfg_model_fname = "%senglishPCFG.ser" % stanford_parser_data_home
            #self.pcfg_model_fname = "%s/englishFactored.ser" % stanford_parser_home
            #self.pcfg_model_fname = "%s/../englishPCFG.July-2010.ser" % stanford_parser_home            
        else:
            self.pcfg_model_fname = pcfg_model_fname


        self.verbose = False
        self.package_lexparser = jpype.JPackage("edu.stanford.nlp.parser.lexparser")
        
        self.package_io = jpype.JPackage("java.io")
        print "name", self.pcfg_model_fname
        self.parser = self.package_lexparser.LexicalizedParser.loadModel()
        self.package = jpype.JPackage("edu.stanford.nlp")

        tokenizerFactoryClass = self.package.process.__getattribute__("PTBTokenizer$PTBTokenizerFactory")
        self.tokenizerFactory = tokenizerFactoryClass.newPTBTokenizerFactory(True, True)


        
        
        self.parser.setOptionFlags(["-retainTmpSubcategories"])




    def printInfo(self):

        Numberer = self.package.util.Numberer
        print ("Grammar\t" +
               `Numberer.getGlobalNumberer("states").total()` + '\t' +
               `Numberer.getGlobalNumberer("tags").total()` + '\t' +
               `Numberer.getGlobalNumberer("words").total()` + '\t' +
               `self.parser.pparser.ug.numRules()` + '\t' +
               `self.parser.pparser.bg.numRules()` + '\t' +
               `self.parser.pparser.lex.numRules()`)

        print "ParserPack is ", self.parser.op.tlpParams.getClass()
        print "Lexicon is ", self.parser.pd.lex.getClass()        
        print "Tags are: ", Numberer.getGlobalNumberer("tags")
        self.parser.op.display()
        print "Test parameters"
        self.parser.op.tlpParams.display();
        self.package_lexparser.Test.display()

    def parseTopN(self, sentence, n):
        """
        Parses the sentence string, returning the tokens, and the parse tree as a tuple.
        tokens, tree = parser.parse(sentence)
        """
        tokens = sentence.split(" ")
        parserQuery = self.parser.parserQuery()

        tf = self.parser.getOp().langpack().getTokenizerFactory();
        tokenizer = tf.getTokenizer(self.package_io.BufferedReader(self.package_io.StringReader(sentence)));
        
        tokens = tokenizer.tokenize()
        try:

            wasParsed = parserQuery.parse(tokens)
        except:
            print "Could not parse ", sentence
            print "tokens", tokens
            raise
        if not wasParsed:
            raise ParserError("Could not parse " + sentence)
        #return tokens, self.parser.getBestParse()
        parses = parserQuery.getKBestPCFGParses(n)
        # print 'parses', parses
        # for parse in parses:
        #     tree = parse.object()
        #     print "******", parse.score()
        #     print tree.taggedYield().toString(False)
        #     print tree
        return tokens, [(p.score(), p.object()) for p in parses]
    
    def parse(self, sentence):
        tokens, parses = self.parseTopN(sentence, n=1)
        return tokens, parses[0]

    def parseToTopNStanfordDependencies(self, sentence, n):
        tokens, trees = self.parseTopN(sentence, n)
        standoffTokens = [standoffFromToken(sentence, token)
                          for token in tokens]
        result = []
        for score, tree in trees:
            result.append(self.treeToStanfordDependencies(sentence, tree, tokens, score))
        return result
                              
        
    def parseToStanfordDependencies(self, sentence):
        return self.parseToTopNStanfordDependencies(sentence, 1)[0]

    def treeToStanfordDependencies(self, sentence, tree, tokens, score=None, collapse_deps=True):
        standoffTokens = [standoffFromToken(sentence, token)
                          for token in tokens]
        posTags = [token.tag() for token in tree.taggedYield()]
        if self.verbose:
            print
            print tree.taggedYield().toString()
            print tree
        egs = self.package.trees.EnglishGrammaticalStructure(tree)
        dependency_list = []
        if collapse_deps:
            egs_dependencies = egs.typedDependenciesCollapsedTree()
        else:
            # egs_dependencies = egs.typedDependencies(includeExtras=False)
            egs_dependencies = egs.allTypedDependencies()
        for dependency in egs_dependencies:
            import pdb
            # pdb.set_trace()
            govStandoff = standoffTokens[dependency.gov().index() - 1]
            depStandoff = standoffTokens[dependency.dep().index() - 1]
            
            dependency_list.append((str(dependency.reln()),
                                    govStandoff,
                                    depStandoff))
            if self.verbose:
                print dependency.reln(),
                print "(", dependency.gov(), dependency.dep(), ")"
        return Dependencies(sentence, standoffTokens, posTags, dependency_list, score)


    def makeTreeClass(self, tree_string):
        """
        The StanfordParser tools want their own particular version of a 'Tree'. This function converts a Penn Treebank tree (as a string) into that class.
        """
        string_reader = jpype.java.io.StringReader(tree_string)
        tree_reader = self.package.trees.PennTreeReader(string_reader, self.package.trees.LabeledScoredTreeFactory())
        return tree_reader.readTree()




