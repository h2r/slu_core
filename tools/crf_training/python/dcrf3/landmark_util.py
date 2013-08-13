import Polygon
from scipy import transpose
from nltk.tokenize import word_tokenize

class landmark:
    def __init__(self, words, XY):
        self.words = words
        self.XY = XY
        self.points = transpose(XY)

    def __repr__(self):
        return "path_len:"+str(len(self.points)) +" words:" + str(self.words)

    def __str__(self):
        return "path_len:"+str(len(self.points)) +" words:" + str(self.words)


def get_landmarks(myannotations): 
    ret_landmarks = []
    
    for i, sent in enumerate(myannotations):
        if(not sent.has_key("path_start")):
            continue
        
        print "i=", i 
        for j in range(len(sent["path_start"])):
            if(len(sent["landmark"][j]) == 0):
                continue

            lmark_words = word_tokenize(sent["SDCs_gt"][j].landmark.text.lower())
            lmark_xy = sent["landmark"][j]
            lmark = landmark(lmark_words, transpose(lmark_xy))
            
            is_contained, index = landmark_contained(lmark, ret_landmarks)
            if(not is_contained):
                if(len(lmark_words) == 0):
                    print "WARNING: no words", lmark_xy
                    continue
                
                ret_landmarks.append(lmark)
    
    #add the null landmark
    ret_landmarks.append(landmark([], []))
    return ret_landmarks


def landmark_contained(landmark, landmarks):
    if(len(landmarks) == 0):
        return False, None
    
    if(len(landmark.points) > 0):
        l_query = Polygon.Polygon(landmark.points)
    else:
        l_query = None
    
    for i, l in enumerate(landmarks):
        if(len(l.points) == 0 and len(landmark.points) == 0):
            return True, i
        elif(len(l.points) == 0 
             or len(landmark.points) == 0):
            continue
        
        l_curr = Polygon.Polygon(l.points)
        l_int = l_curr&l_query
        l_un = l_curr|l_query
        
        if(l_un.area() == 0.0):
            continue
        
        if((l_int.area()/l_un.area()) > 0.25):
            return True, i

    return False, None
