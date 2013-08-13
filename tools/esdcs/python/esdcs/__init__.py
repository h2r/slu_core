from dataStructures import ExtendedSdc



def isEsdc(obj):
    if isinstance(obj, ExtendedSdc):
        return True
    elif (isinstance(obj, list) and
          all([isEsdc(x) for x in obj])):
        return True
    elif (isinstance(obj, dict) and
          all([isEsdc(x) for x in obj.values()])):
        return True
    else:
        return False

          


