import sys, re
import csv
from collections import defaultdict
from math import exp, pow, log
from collections import Counter

unknown_token = "<UNK>"  # unknown word token.


''' utililty functions for preprocessing and reading in data '''


''' returns an array of the sentances in the given file '''
def get_sents(file_name):
    sents = list()
    with open(file_name, 'r') as f:
        sents = [s.strip('\n') for s in f.readlines()]
    return sents


''' returns a dictionary that maps pairs of words (es, en) to the log proability
    of that word alignment
'''
def get_word_translations(file_name):
    reader = None
    translations = defaultdict(lambda : defaultdict(lambda : float("-inf")))
    with open(file_name, 'r') as f:
        reader = csv.reader(f, delimiter=' ')
        for row in reader:
            trg, src, prob = row
            translations[src][trg] = log(float(prob))

    return translations


''' Implementation of a statistical phrase based translator '''
class Translator(object):

    def __init__(self, src_sents, trg_sents, word_alignments):
        self._src_sents           = src_sents
        self._trg_sents           = trg_sents
        self._word_alignments     = word_alignments
        self._word_aligner        = None
        self._phrase_alignments   = None
        # phrase translation table: phrase_translations[(f, e)] = count(f,e) / num phrase pairs
        self._phrase_translations = None


    ''' trains the phrase based translator '''
    def train(self):
        # train the translator
        # train the decoder
        return None

    ''' returns the hypothesis in the given stack with the lowest cost'''
    def beam_search(stack):
        # get the least cost hypotesis
        # look through the expansions for the hypotesis
        return None

    ''' returns a list of expanisions for the given hypotheisis '''
    def expanisions_for_hypothesis(hyp):
        return None

    ''' returns the cost for the given hypothesis '''
    def cost(hyp):
        return None

    ''' returns an array of translated sentances for the given source sentances '''
    def translate(src_sents):
        return None


''' BLEU evaluation '''

def bleu_score(pred_sents, trg_sents):
    return None


def main():
    # 1957664 sentances total
    # get the sentances in the corpus
    en_sents = get_sents('data/tok.low.en')
    es_sents = get_sents('data/tok.low.es')

    # 1,762,664 is roughly %90
    en_train_set = en_sents[1762664:]
    es_train_set = es_sents[1762664:]

    #create vocab
    #vocab =

    # 195,000 is roughly %10
    es_test_set = es_sents[:195000]
    en_test_set = en_sents[:195000]

    # we may need to filter this using vocab to prevent having info we should have
    # read in the word alignment data
    word_translations = get_word_translations('data/actual.ti.final')

    # create a translator
    translator = Translator(en_train_set, es_train_set, word_alignments)
    translator.train()
    predictions = translate(spanish)
    bleu = bleu_score(predictions, en_test_set)

main()
