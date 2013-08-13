from nltk.corpus import wordnet as wn


def get_word_similarity_wup(worda, wordb):
	"""
	find similarity between two words
	"""
	wordasynsets = wn.synsets(worda)
	wordbsynsets = wn.synsets(wordb)

	#print worda, wordb
	#print wordasynsets
        #print wordbsynsets
	probs_wup = []
	for w in wordasynsets:
            for w2 in wordbsynsets:
		    probs_wup.append(w.wup_similarity(w2))
        if(len(probs_wup) == 0):
            return 10e-100

	return max(probs_wup)


def get_word_similarity_path(worda,wordb):
	"""
	find similarity between two words
	"""
	wordasynsets = wn.synsets(worda)
	wordbsynsets = wn.synsets(wordb)

	#print worda, wordb
	probs_path = []
	for w in wordasynsets:
            for w2 in wordbsynsets:
                probs_path.append(w.path_similarity(w2))

        if(len(probs_path) == 0):
            return 10e-100

	return max(probs_path)





if __name__ == "__main__":
	print "---------------------------------"
        print "field, cow"
	get_word_similarity_path('field','cow')
	get_word_similarity_wup('field','cow')
	print "---------------------------,------"
        print "stapler, cow"
	get_word_similarity_path('stapler','cow')
	get_word_similarity_wup('stapler','cow')
	print "---------------------------------"
        print "sky, cow"
	get_word_similarity_path('sky','cow')
	get_word_similarity_wup('sky','cow')
	print "---------------------------------"
        print "cat, walk"
	get_word_similarity_path('cat','walk')
	get_word_similarity_wup('cat','walk')
	print "---------------------------------"
        print "cricket, cockroach"
	get_word_similarity_path('cricket','cockroach')
	get_word_similarity_wup('cricket','cockroach')
	print "---------------------------------"
        print "corridor, hallway"
	get_word_similarity_path('corridor','hallway')
	get_word_similarity_wup('corridor','hallway')
	print "---------------------------------"
        print "desk, table"
	get_word_similarity_path('desk','table')
	get_word_similarity_wup('desk','table')
	print "---------------------------------"
        print "monitor, screen"
	get_word_similarity_path('monitor','screen')
	get_word_similarity_wup('monitor','screen')

