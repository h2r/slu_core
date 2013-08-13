from nltk.metrics.distance import edit_distance
from esdcs import esdcIo
import yaml

def fractionOfMatches(esdc1, esdc2):
    flattened_esdcs1 = set(esdc1.flattenedEsdcs)
    flattened_esdcs2 = set(esdc2.flattenedEsdcs)

    total = len(flattened_esdcs1) + len(flattened_esdcs2)
    matches = 0.0
    for esdc in flattened_esdcs1:
        if esdc in flattened_esdcs2:
            matches += 1
    for esdc in flattened_esdcs2:
        if esdc in flattened_esdcs1:
            matches += 1

            
    return matches / total

def editDistance(esdc1, esdc2):
    
    yaml1 = esdcIo.toYaml(esdc1)
    yaml2 = esdcIo.toYaml(esdc2)

    str1 = yaml.dump(yaml1)
    str2 = yaml.dump(yaml2)

    score = edit_distance(str1, str2)

    score = float(score) / max([len(str1), len(str2)])
    return 1-score


