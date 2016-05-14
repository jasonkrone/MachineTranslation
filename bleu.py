''' bleu.py by Jason Krone and Nick Yan for Comp150
'''

from collections import defaultdict, Counter
from math import exp, pow, log
import sys


class Bleu(object):

    def __init__(self, predictions_file, target_file):
        self._preds  = self._get_lines(predictions_file)
        self._target = self._get_lines(target_file)

    ''' returns the lines in the given file '''
    def _get_lines(self, file_name):
        lines = None
        with open(file_name, 'r') as f:
            lines = [line.split() for line in f.readlines()]
        return lines

    ''' returns the bleu score using 1gram -> n-grams for preds and target '''
    def score(self, n):
        score = 0.0
        w = float(1) / n
        # use 1gram -> ngram precision
        for i in xrange(1, n+1):
            ngram_matches = 0
            pred_grams = self._get_ngram_sent_counts(i, self._preds)
            trg_grams  = self._get_ngram_sent_counts(i, self._target)
            # get the number of possible matches
            candidate_matches = 0
            for sent in trg_grams:
                candidate_matches += sum(sent.values())
            # compute the number of ngram matches sentence by sentence
            for pred_sent_counts, trg_sent_counts in zip(pred_grams, trg_grams):
                # get clipped counts
                ngram_matches += sum([min(trg_sent_counts[ng], pred_sent_counts[ng]) for ng in pred_sent_counts])
            # add weighted, log of modified precision score
            if ngram_matches:
                pr = float(ngram_matches) / candidate_matches
                score += log(pr) * w
            else: # the log(0) -> -infinity and exp(-inf) = 0
                return 0

        # effective reference length for corpus
        r = sum([len(s) for s in self._target])
        c = sum([len(s) for s in self._preds])
        # brevity penalty
        bp = 1 if c > r else exp((1 - r) / c)
        print 'bp:', bp
        return bp * exp(score) if score != 0 else 0


    def _get_ngram_sent_counts(self, n, corpus):
        ngram_sent_counts = list()
        # fill sent counts
        for sent in corpus:
            sent_counts = defaultdict(lambda : int())
            ngrams  = self._ngrams_for_sent(n, sent)
            for ng in ngrams:
                sent_counts[ng] += 1
            ngram_sent_counts.append(sent_counts)

        return ngram_sent_counts

    # taken from http://locallyoptimal.com/blog/2013/01/20/elegant-n-gram-generation-in-python/
    def _ngrams_for_sent(self, n, sent):
        return zip(*[sent[i:] for i in range(n)])


# read in predictions and target files from command line
def main():
    if len(sys.argv) != 3:
        print 'usage: python bleu.py predictions_file target_file'
        return

    bleu  = Bleu(sys.argv[1], sys.argv[2])
    score = bleu.score(4)
    print 'bleu score: ', score

main()
