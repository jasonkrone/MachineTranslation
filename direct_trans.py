# Direct Translation (for Machine Translation)

# COMP 150: Natural Language Processing
# Jason Krone & Nicholas Yan
# 5/11/16

##################################################################################################
#                                                                                                #
#                                        DIRECT TRANSLATION                                      #
#                                                                                                #
##################################################################################################

import sys
from collections import defaultdict
import csv
import string
from utilities import get_word_translations, tokenize, get_datasets

class DirectTrans:

	# init
    #
    # args:     translation_table   dict, takes a first key (the word) and return a list of
    #                               all possible translations for that first key
    #           prune               the pruning method (THRESHOLD or HISTOGRAM)
    #           pthresh             the pruning threshold

    def __init__(self, translation_table):

        self.all_translations = translation_table
        
    def translate(self, source_sent):

    	trans_sent = []

    	for word in source_sent:

    		# (word, prob)
    		best_trans = (None, None)

    		for trans in self.all_translations[word]:
    			prob = self.all_translations[word][trans]
    			if best_trans[1] is None or prob > best_trans[1]:
    				best_trans = (trans, prob)

    		if best_trans[0] is not None:
    			trans_sent.append(best_trans[0])

    	return trans_sent

def main():

	translation_table = get_word_translations("100kword_trans.csv")
	translator = DirectTrans(translation_table)

	english = tokenize("data/100ktok.low.en")
	spanish = tokenize("data/100ktok.low.es")

	training_set, test_set, translated_set = get_datasets(english, spanish)

	test_output = open('trans_direct.txt','w')

	for i in range(len(test_set)):
		print i
		test_output.write(' '.join(translator.translate(test_set[i])) + "\n")

	test_output.close()

if __name__ == "__main__": 
    main()