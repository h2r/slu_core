def correctStandoffOffset(standoff, new_entire_text, offset):
    new_standoff = TextStandoff(new_entire_text, 
                                (standoff.range[0] + offset,
                                 standoff.range[1] + offset))
    assert new_standoff.text == standoff.text
    return new_standoff
    
    
def correctStandoffImmutable(sentenceStandoff, standoff):
    """
    Makes the standoff relative to the larger standoff object,
    returning the new standoff.
    """
    new_standoff = TextStandoff.copy(standoff)
    correctStandoff(sentenceStandoff, new_standoff)
    return new_standoff

def correctStandoff(sentenceStandoff, standoff):
    """
    Makes the standoff relative to the larger standoff object. 

    It MUTATES the standoff.  It CHANGES the hash code.
    """
    if standoff.entireText != sentenceStandoff.entireText:
        
        old_text = standoff.text
        standoff.entireText = sentenceStandoff.entireText
        start, end = standoff.range
        standoff.range = (start + sentenceStandoff.start,
                          end + sentenceStandoff.start)
        
        cropped_text = standoff.entireText[standoff.range[0]:
                                               standoff.range[1]]
        assert cropped_text == old_text,\
                                       ("Incorrect sentenceStandoff range",
                                        cropped_text)
                                        
    return standoff

def correctStandoffs(sentenceStandoff, standoffs):
    """
    Makes the standoff relative to the larger standoff object. 

    It MUTATES the standoff.  It CHANGES the hash code.
    """
    for  standoff in standoffs:
        correctStandoff(sentenceStandoff, standoff)
    return standoffs

class FakeStandoff:
    @staticmethod
    def standoffs_from_string(string):
        return [FakeStandoff(s) for s in string.split()]
        
    def __init__(self, string):
        self.text = string
    def __str__(self):
        return self.text

class TextStandoff:
    @staticmethod
    def entireText(text):
        return TextStandoff(text, (0, len(text)))

    @staticmethod
    def copy(standoff):
        return TextStandoff(standoff.entireText, standoff.range)

    @staticmethod
    def join(standoff, other):
        """
        Combine two standoffs from a given entireText and find the standoff spanning 
        both of them. This will be equivalent to the union of their text fields if
        their ranges are adjacent. 

        This returns a *new* TextStandoff object.
        """
        assert standoff.entireText == other.entireText,\
                "entireText must match to join standoffs"
        return TextStandoff(standoff.entireText,
                            [min(standoff.start, other.start), 
                             max(standoff.end, other.end)])
        
    def __init__(self, text, range_tuple):
        self.entireText = text

        self.range = range_tuple

    def ensureString(self):
        """
        Returns a new TextStandoff where entireText is a string and
        not unicode or something else.
        """
        return TextStandoff(str(self.entireText), self.range)
        
    def asPrimitives(self):
        return (self.entireText, self.range)
    
    @staticmethod
    def fromPrimitives(args):
        return TextStandoff(*args)
        
    def isNull(self):
        return self.range == (0, 0)
    
    @property
    def text(self):
        start, end = self.range
        return self.entireText[start:end]
    @property
    def length(self):
        start, end = self.range
        return end - start
    @property
    def end(self):
        start, end = self.range
        return end
    @property
    def start(self):
        start, end = self.range
        return start

    def overlaps(self, standoff):
        if self.start < standoff.end and standoff.start < self.end:
            return True
        else:
            return False
    def contains(self, standoff):
        start, end = standoff
        return self.start <= start and self.end >= end
    def before(self, standoff):
        if self.end <= standoff.start:
            return True
        else:
            return False
    def degreeOfOverlap(self, standoff):
        """
        Returns the size of the overlapping range of two tags. Returns
        zero if they do not overlap.
        """
        start, end = standoff
        if self.overlaps(standoff):
            return min(end, self.end) - max(start, self.start)
        else:
            return 0

    def __iter__(self):
        return iter((self.start, self.end))
    def toXml(self, standoff):
        standoff.setAttribute("start", str(self.start))
        standoff.setAttribute("end", str(self.end))

    def __repr__(self):
        return 'TextStandoff("%s", (%d, %d))' % (self.entireText, self.start, self.end)

    def __str__(self):
        return '("%s", (%d, %d))' % (self.text, self.start, self.end)

    def __eq__(self, obj):
        if isinstance(obj, TextStandoff):
            if self.range == obj.range and self.entireText == obj.entireText:
                return True
        return False

    def __hash__(self):
        return hash(self.entireText) * 17 + hash(self.range)




        
