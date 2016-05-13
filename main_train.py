import sys
from beam_search import BeamSearch

import csv
from collections import defaultdict
import re
from math import log, exp

import string

def main():

    english = tokenize("data/100ktok.low.en")
    spanish = tokenize("data/100ktok.low.es")

    training_set, test_set, translated_set = get_datasets(english, spanish)
    translations = get_word_translations("3000_trans.txt")
    search = BeamSearch(training_set, translations)

    test_output = open('trans.txt','w')
    true_output = open('true.txt','w')

    for i in range(len(test_set)):
        print i
        test_output.write(' '.join(search.translate(test_set[i])) + "\n")
        true_output.write(' '.join(translated_set[i]) + "\n")

    test_output.close()
    true_output.close()

def tokenize(filename):

    tokens = []

    file_name = filename
    with open(file_name, 'r') as f:
        for line in f:

            # http://stackoverflow.com/questions/23317458/how-to-remove-punctuation
            tok_line = " ".join("".join([" " if ch in string.punctuation else ch for ch in line]).split()).split()

            tokens.append(tok_line)

    return tokens

def get_datasets(english, spanish):

    training_set = english[:95000]
    test_set = spanish[95000:]
    translated_set = english[95000:]

    return training_set, held_out_set, test_set, translated_set

def get_word_translations(file_name):
    reader = None
    translations = defaultdict(lambda : defaultdict(lambda : float("-inf")))
    with open(file_name, 'r') as f:
        reader = csv.reader(f, delimiter=' ')
        for row in reader:
            trg, src, prob = row
            translations[trg][src] = float(prob)

    return translations

if __name__ == "__main__": 
    main()