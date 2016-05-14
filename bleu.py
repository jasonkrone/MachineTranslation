''' bleu.py by Jason Krone and Nick Yan for Comp150
'''

from collections import defaultdict, counter
from math import exp, pow, log
import sys

START_TOKEN = '<S>'
END_TOKEN   = '</S>'

class Bleu(object):

    def __init__(self, predictions_file, target_file):
        self._preds  = self._get_lines(predictions_file)
        self._target = self._get_lines(target_files)

    ''' returns the lines in the given file '''
    def _get_lines(self, file_name):
        lines = None
        with open(file_name, 'r') as f:
            lines = [line.split() for line in f.readlines()]
        return lines

    ''' returns the bleu score using 1gram -> n-grams for preds and target '''
    def score(self, n):
        score = 0.0
        # use 1gram -> ngram precision
        for i in xrange(1, n):
            ngram_matches = 0
            pred_grams = self._get_ngram_sent_counts(n, self._preds)
            trg_grams  = self._get_ngram_sent_counts(n, self._target)
            candidate_matches = sum([count for sent in trg_grams for (ngram, count) in sent.items()])
            # compute the number of ngram matches sentence by sentence
            for pred_sent_counts, trg_sent_counts in zip(pred_grams, trg_grams):
                # get clipped counts
                ngram_matches += sum([min(trg_sent_counts[ngram], pred_sent_counts[ngram]) for ngram in pred_sent])
            # add weighted, log of modified precision score
            score += log(float(ngram_matches) / candidate_matches)) * 1/n
        # effective reference length for corpus
        r = sum([len(s) for s in self._target])
        c = sum([len(s) for s in self._preds])
        # brevity penalty
        bp = 1 if c > r else exp((1 - r) / c)
        return bp * exp(score)

    def _get_ngram_sent_counts(self, n, corpus):
        ngram_sent_counts = list()

        # pad sentences
        start_padding = [START_TOKEN] * n-1
        end_padding   = [END_TOKEN] * n-1
        for sent in corpus:
            sent[0:0] = start_padding
            sent.extend(end_padding)

        # fill sent counts
        for pad_sent in corpus:
            sent_counts = defaultdict(lambda : int())
            ngrams  = ngrams_for_sent(pad_sent)
            for ng in ngrams:
                sent_counts[ng] += 1
            ngram_sent_counts.append(sent_counts)

        return ngram_sent_counts

    # taken from http://locallyoptimal.com/blog/2013/01/20/elegant-n-gram-generation-in-python/
    def _ngrams_for_sent(self, n, sent):
        zip(*[sent[i:] for i in range(n)])


# read in predictions and target files from command line
def main():
    if len(sys.argv) != 3:
        print 'usage: python bleu.py predictions_file target_file'

    bleu  = Bleu(sys.argv[1], sys.argv[2])
    score = bleu.score(4)
    print 'bleu score: ', score


