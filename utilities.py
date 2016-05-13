# Utility Functions (for Machine Translation)

# COMP 150: Natural Language Processing
# Jason Krone & Nicholas Yan
# 5/11/16

##################################################################################################
#                                                                                                #
#                                              UTILITIES                                         #
#                                                                                                #
##################################################################################################

import csv
import sys
import string
from collections import defaultdict

def get_word_translations(file_name):
    reader = None
    translations = defaultdict(lambda : defaultdict(lambda : float("-inf")))
    with open(file_name, 'r') as f:
        reader = csv.reader(f, delimiter=' ')
        for row in reader:
            trg, src, prob = row
            translations[trg][src] = float(prob)

    return translations

def tokenize(filename):

    tokens = []

    file_name = filename
    with open(file_name, 'r') as f:
        for line in f:

            # http://stackoverflow.com/questions/23317458/how-to-remove-punctuation
            tok_line = " ".join("".join([" " if ch in string.punctuation else ch for ch in line]).split()).split()

            # ensure there are no empty lines in the input data file
            if tok_line:
            	tokens.append(tok_line)

    return tokens

def get_datasets(english, spanish):

    training_set = english[:99900]
    test_set = spanish[:100]
    translated_set = english[:100]

    return training_set, test_set, translated_set