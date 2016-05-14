''' symmetrizer.py by Jason Krone and Nick Yan for Comp150
'''

from collections import defaultdict, Counter
from math import exp, pow, log
import copy
import codecs
import csv

UNKNOWN_TOKEN = "<UNK>"
MAX_PHRASE_LEN = 7
ALIGN_START_TOKEN = '({'
ALIGN_END_TOKEN   = '})'


class Symmetrizer(object):

    def __init__(self, e2f, f2e, e_corpus, f_corpus):
        self._e2f = e2f
        self._f2e = f2e
        self._ecorp = e_corpus
        self._fcorp = f_corpus
        # translations[foreign_phrase][englist_phrase] = log_prob
        self.translations = defaultdict((lambda : defaultdict(lambda : float('-inf'))))
        self.alpha = float()


    ''' writes self.translations to the given file '''
    def write_translations_to_file(self, file_name):
        rows = list()
        for f in self.translations:
            for e in self.translations[f]:
                prob = self.translations[f][e]
                # encode to take care of special chars (accents on spanish chars ...etc)
                rows.append([f.encode("utf-8"), e.encode("utf-8"), prob])

        with open(file_name, 'w+') as f:
            writer = csv.writer(f, delimiter=' ')
            writer.writerows(rows)


    ''' fills the phrase translation table using e2f and f2e alignments'''
    def symmetrize(self):
        phrase_pairs = defaultdict((lambda : defaultdict(lambda : int())))
        zp = zip(self._e2f, self._f2e, self._ecorp, self._fcorp)

        # loop through sentence alignements and sentences
        for (e2f_align, f2e_align, e_sent, f_sent) in zp:
            dim = (len(e_sent), len(f_sent))
            alignment = self._grow_diag_final(e2f_align, f2e_align, dim)
            phrases   = self._extract_phrase_pairs(alignment, e_sent, f_sent)
            # update phrase pair counts
            for _, e, f in phrases:
                phrase_pairs[e][f] += 1

        # fill the translation table
        for e in phrase_pairs:
            e_phrase_pairs = phrase_pairs[e]
            e_count = len(e_phrase_pairs)
            for f in e_phrase_pairs:
                prob = float(e_phrase_pairs[f]) / e_count
                self.translations[f][e] = log(prob)

        # prune table -- limit translations options to 20 for a phrase
        for f in self.translations:
            trans = self.translations[f].items()
            # get the 20 with the highest probabilty
            trans = sorted(trans, key= lambda x: x[1], reverse=True)[:20]
            self.translations[f] = dict(trans)

        # note: can potentially imporve scoring by smoothing
        # can use chi squared stats based pruning (prob not this)


    ############# FUNCTIONS FOR GROW-DIAG-FINAL ##############

    ''' returns the alignment created from e2f and f2e using the grow-diag-final heuristic'''
    def _grow_diag_final(self, e2f_align, f2e_align, dim):
        intersect = e2f_align.intersection(f2e_align)
        union     = e2f_align.union(f2e_align)
        alignment = self._grow_diag(intersect, union, dim)
        alignment = self._final(e2f_align, alignment)
        alignment = self._final(f2e_align, alignment)
        return alignment


    ''' grows the alignment A by selectively adding elems from union '''
    def _grow_diag(self, A, union, dim):
        points_added = True
        e_aligned = [e for (e, _) in A]
        f_aligned = [f for (_, f) in A]

        while points_added:
            points_added = False
            A_copy = copy.copy(A)
            for aligned_pair in A_copy:
                for (e_new, f_new) in self._neighbors(aligned_pair, dim):
                    # e-new not aligned or f-new not aligned
                    if (e_new not in e_aligned or f_new not in f_aligned) and (e_new, f_new) in union:
                        A.add((e_new, f_new))
                        e_aligned.append(e_new)
                        f_aligned.append(f_new)
                        points_added = True
        return A


    ''' returns list of possible neighboring alignments '''
    def _neighbors(self, aligned_pair, dim):
        e_len, f_len = dim
        neighboring = [(-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        x, y = aligned_pair
        points = [(x + s, y + t) for s, t in neighboring]
        return filter(lambda p : (0 <= p[0] <= e_len-1) and (0 <= p[1] <= f_len-1), points)


    ''' adds select points from a to the alignment A'''
    def _final(self, a, A):
        e_aligned = [e for (e, _) in A]
        f_aligned = [f for (_, f) in A]
        # words aligned in a
        for (e_new, f_new) in a:
            if e_new not in e_aligned or f_new not in f_aligned:
                A.add((e_new, f_new))
                e_aligned.append(e_new)
                f_aligned.append(f_new)
        return A


    ############# FUNCTIONS FOR EXTRACTING PHRASES ##############


    ''' returns the set of phrase pairs in the given alignment A'''
    def _extract_phrase_pairs(self, A, e_sent, f_sent):
        bp = list()
        e_len, f_len = len(e_sent), len(f_sent)

        for e_start in xrange(e_len):
            for e_end in xrange(e_start, e_len):
                # find the minimally matching foreign phrase
                f_start, f_end = f_len-1, -1
                for (e, f) in A:
                    if e_start <= e <= e_end:
                        f_start = min(f, f_start)
                        f_end   = max(f, f_end)
                bp.extend(self._extract(A, e_sent, f_sent , e_start, e_end, f_start, f_end))
        return bp


    ''' returns the set of phrase pairs within A[e_start->e_end][f_start->f_end]'''
    def _extract(self, A, e_sent, f_sent, e_start, e_end, f_start, f_end):
        E = set()
        # check that there is at least one alignment pair
        if f_end < 0:
            return E
        # check if alignment points violate consistency
        for e, f in A:
            if (f_start <= f <= f_end) and (e < e_start or e > e_end):
                return E

        # add phrase pairs including unaligned f
        fs = f_start
        f_len = len(f_sent)
        f_aligned = [f for (_, f) in A]
        while True:
            fe = f_end
            while True:
                try:
                    # add phrase pair ([e_start, e_end], [fs, fe]) to E
                    e_phrase = ' '.join(e_sent[i] for i in xrange(e_start, e_end+1))
                    f_phrase = ' '.join(f_sent[i] for i in xrange(fs, fe+1))
                except: # debug output
                    print 'A', A
                    print 'e_sent: ', e_sent
                    print 'f_sent: ', f_sent
                    print 'f_start: ', f_start
                    print 'f_end: ', f_end

                if (fe-fs) <= MAX_PHRASE_LEN and (e_end-e_start) <= MAX_PHRASE_LEN:
                    E.add(((e_start, e_end+1), e_phrase, f_phrase))
                fe += 1
                if fe in f_aligned or fe == f_len:
                    break
            fs -= 1
            if fs in f_aligned or fs < 0:
                break
        return E


########### FUNCTIONS FOR READING IN DATA FROM GIZA ALIGNMENT5 FILES #################


''' creates an instance of Symmetrizer using the given alignment files
    Note: uses words in f_corp and e_corp that occur more than once as vocab
'''
def symmetrizer_from_alignment_files(e2f_file, f2e_file):
    e2f, f_corpus = alignment_trg_corp(e2f_file, True)
    f2e, e_corpus = alignment_trg_corp(f2e_file, False)

    e2f_clean, f2e_clean = list(), list()
    f_corpus_clean, e_corpus_clean = list(), list()

    # clean the data
    for e_align, f_align, e_sent, f_sent in zip(e2f, f2e, e_corpus, f_corpus):
        e_len, f_len = len(e_sent), len(f_sent)
        if alignment_in_bounds(e_align, e_len, f_len) and alignment_in_bounds(f_align, e_len, f_len):
            e2f_clean.append(e_align)
            f2e_clean.append(f_align)
            e_corpus_clean.append(e_sent)
            f_corpus_clean.append(f_sent)

    return Symmetrizer(e2f_clean, f2e_clean, e_corpus_clean, f_corpus_clean)

def vocab_for_corpus(corpus):
    words   = [w for sent in corpus for w in sent]
    counter = Counter(words)
    vocab   = set([w for (w, c) in counter.most(common) if c > 1])

''' determines if the alignment points are consitent with the given sentence lengths '''
def alignment_in_bounds(A, e_len, f_len):
    for (e, f) in A:
        if e >= e_len or e < -1 or f < -1 or f >= f_len:
            return False
    return True


''' returns the alignment and target corpus for the given alignment file'''
def alignment_trg_corp(align_file, src_is_english):
    corpus = list()
    alignments = list()

    f = codecs.open(align_file, encoding='utf-8', mode='r')
    lines = f.readlines()
    for i, line in enumerate(lines):
        # target sentence line
        if i % 3 == 1:
            sent = ['NULL'] + line.split()
            corpus.append(sent)
        # alignment line
        elif i % 3 == 2:
            alignments.append(alignment_from_line(line, src_is_english))
    f.close()

    return alignments, corpus


''' returns the parsed word alignment set from the given line '''
def alignment_from_line(line, src_is_english):
    cur_word_idx = -1
    alignment = set()
    tokens = line.split()
    in_alignment = False

    for t in tokens:
        if t == ALIGN_START_TOKEN:
            in_alignment = True
        elif t == ALIGN_END_TOKEN:
            in_alignment = False
        elif in_alignment and t.isdigit():
            # subtract 1 because we are 0 indexing and giza 1 indexes
            if src_is_english:
                alignment.add((cur_word_idx, int(t)-1))
            else:
                alignment.add((int(t)-1, cur_word_idx))
        elif in_alignment is False:
            # we hit a token
            cur_word_idx += 1

    return alignment


''' replaces tokens that appear only once with the UNKNOWN_TOKEN '''
def prep_alignment_file(file_name):
    f = codecs.open(file_name, encoding='utf-8', mode='r+')
    lines    = f.readlines()
    f.close()
    # get the text lines from file
    corp     = [lines[i] for i in xrange(len(lines)) if i % 3 == 1]
    corp     = [l.split() for l in corp] # split on spaces
    tokens   = [t for l in corp for t in l] # extract tokens
    counter  = Counter(tokens)
    # include tokens that appear more than once
    vocab    = [t for (t, c) in counter.most_common() if c > 1]
    # replace tokens that occur once with unknown token
    prep_corp  = [[t if t in vocab else UNKNOWN_TOKEN for t in l] for l in corp]
    prep_lines = [' '.join(prep_corp[i/3]) if i % 3 == 1 else lines[i] for i in xrange(len(lines))]

    print prep_lines



    '''
    #rows.append([f.encode("utf-8"), e.encode("utf-8"), prob])
    with open('prep_' + file_name, 'w+') as f:
        for l in prep_lines:
            f.write(l)
    with open('prep_' + file_name + '.vocab', 'w') as v:
        for w in vocab:
            v.write(w + '\n')
    f.close()
    '''

def main():
    prep_alignment_file('100en_to_es.VA3.final')
    '''
    sym = symmetrizer_from_alignment_files('data/3000en_to_es.VA3.final', 'data/3000es_to_en.VA3.final', vocab)
    #sym.symmetrize()
    counts = defaultdict((lambda : defaultdict(lambda : int())))

    for e_sent, f_sent, e2f_align, f2e_align in zip(sym._ecorp, sym._fcorp, sym._e2f, sym._f2e):
        alignment = sym._grow_diag_final(e2f_align, f2e_align, (len(e_sent),len(f_sent)))
        for e, f in alignment:
            counts[e_sent[e]][f_sent[f]] += 1

        # fill the translation table
        for e in counts:
            e_word_pairs = counts[e]
            e_count = len(e_word_pairs)
            for f in e_word_pairs:
                prob = float(e_word_pairs[f]) / e_count
                sym.translations[f][e] = log(prob)

    sym.write_translations_to_file('3000_word_trans.txt')
    '''

    # read in the first 100 tokenized sentences
    # e_corp = readlines.split()
    # f_corp = readlines.split()
    # e2f alignments
    # f2e alignments

main()
