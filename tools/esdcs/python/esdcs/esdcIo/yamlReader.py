#!/usr/bin/env python
import yaml
from esdcs.dataStructures import ExtendedSdc, wrapValueInList, \
     objectifyLandmarks, addEmptyFigures, objectifyFiguresOfEvents, \
     ExtendedSdcGroup
from standoff import TextStandoff
import re
from tokenizer import IndexedTokenizer

def isWordList(argValue):
    if isinstance(argValue, list) and len(argValue) > 0:
        if isinstance(argValue[0], list):
            return True
    return False
def isEsdc(argValue):
    if isinstance(argValue, dict):
        return True
    if isinstance(argValue, list) and len(argValue) > 0:
        if isinstance(argValue[0], dict):
            return True
    return False

def handleEsdcContents(argMap, entireText):
    outputDict = {}
    for argName, argValue in argMap.iteritems():
        assert argName in ExtendedSdc.fieldNames, ("Arg " + `argName` +
                                                   " not in names." +
                                                   " Value: " + `argValue`)
        if argName  == "id":
            outputDict["esdc_id"] = argValue
        elif isinstance(argValue, str):
            matches = list(re.finditer(re.escape(argValue), entireText))
            if len(matches) == 1:
                match = matches[0]
                tokens = []
                matchText = match.group()
                currentIndex = 0
                for token in matchText.split():
                    # we've ensured the index both exists and is unique.
                    tokenIdx = matchText[currentIndex:].index(token) + currentIndex
                    standoff = TextStandoff(entireText,
                                            (match.start() + tokenIdx, match.start()+ tokenIdx + len(token)))
                    currentIndex = tokenIdx + len(token)
                    tokens.append(standoff)
                outputDict[argName] = tokens                      
            else:
                candidates = [[match.start(), match.end()] for match in matches]
                token = argValue
                tokenizer = IndexedTokenizer()
                for candidate in candidates:
                    print "candidate", candidate
                    for standoff in tokenizer.tokenize(argValue):
                        print "- -", standoff.text
                        start_idx = standoff.start
                        print "  - [%d, %d]" % (candidate[0] + start_idx, 
                                                candidate[0] + start_idx + len(token))
                        
                        
                raise ValueError("Must provide indices for token: '" +
                                 argValue + "' in text '" +
                                 entireText + "'."
                                 " matches: " + `candidates`)



        elif isEsdc(argValue):
            outputDict[argName] = list(fromYaml(entireText, argValue))

        elif isWordList(argValue):
            tokens = []
            try:
                for token, (start, end) in argValue:
                    substring = entireText[start:end]
                    if substring != token:
                        print "candidates"
                        for match in re.finditer(token, entireText):
                            print [match.start(), match.end()]
                        
                        raise ValueError("Token '" + token + "' must correspond" +
                                         " to index " + `(start, end)` +
                                         "and not '" + substring + "'.")
                    tokens.append(TextStandoff(entireText, (start, end)))
            except:
                print "Problem with", argValue
                raise
            outputDict[argName] = tokens

        else:
            raise ValueError("Must be strings or ESDCs: " + `argValue`)

    return outputDict

def handleEsdc(esdcYaml, entireText):
    assert len(esdcYaml) != 0, esdcYaml
    assert isinstance(esdcYaml, dict), (esdcYaml, esdcYaml.__class__)
    esdcType = esdcYaml.keys()[0]
        
    argMap = esdcYaml[esdcType]

    try:
        return esdcType, handleEsdcContents(argMap, entireText)
    except:
        print "arg", argMap
        raise

def parse(yaml_str):
    return fromYaml(*yaml.load(yaml_str))

def fromYaml(entireText, esdcsYaml, use_ids=False):
    """
    Reads a list of esdcs as yaml (maps, lists, strings, as recovered
    from yaml.load), and makes them into proper ESDCs.

    It makes the following conversions:

    * Landmarks that are strings are converted to OBJECT esdcs
      automatically.

    * It parses tokens with ranges, to build standoff tags.

    * Tokens without ranges are automatically converted to standoffs.
      An error is raised if this cannot be done uniquely.  Then the
      token must be specified with a range.
    """
    esdcsYaml = wrapValueInList(esdcsYaml)
    esdcs = []
    for esdcYaml in esdcsYaml:
        try:
            esdcType, outputDict = handleEsdc(esdcYaml, entireText)
            esdcs.append(ExtendedSdc(esdcType, **outputDict))
        except:
            print "Trouble with", esdcYaml
            print "entire text", entireText
            raise
    objectifyLandmarks(esdcs)
    objectifyFiguresOfEvents(esdcs)
    addEmptyFigures(esdcs)

    return ExtendedSdcGroup(esdcs, entireText, use_ids=use_ids)

    
    
        
    

class AnnotatedSentence:
    def __init__(self, sentence, annotation):
        self.sentence = sentence
        self.esdcs = fromYaml(self.sentence, annotation)

    def __repr__(self):
        return """AnnotatedSentence("%s", "%s")""" % (self.sentence, self.esdcs)

def load(annotation_fname):

    with open(annotation_fname) as f:
        annotations = yaml.load(f, Loader=yaml.CLoader)
        
    annotations = [AnnotatedSentence(sentence, esdcYaml)
                   for sentence, esdcYaml in annotations]
                   
    return annotations

    

