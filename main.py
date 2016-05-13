import sys
from beam_search import BeamSearch

import csv
from collections import defaultdict
import re
from math import log, exp

import string

def main():

    english = tokenize("100lines/corp.en")
    spanish = tokenize("100lines/corp.es")

    training_set, held_out_set, test_set = get_datasets(english, spanish)
    translations = get_word_translations("3000_trans.txt")
    search = BeamSearch(training_set, held_out_set, translations)

    print search.translate(test_set[8])

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

    training_set = []
    held_out_set = []
    test_set = []

    for (i, line) in enumerate(english, start=0):
        if i < 60:
            training_set.append(line)
        elif i < 80:
            held_out_set.append(line)

    for (i, line) in enumerate(spanish, start=0):
        # if i > 80:
            test_set.append(line)

    return training_set, held_out_set, test_set

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