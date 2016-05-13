''' symmetrizer.py by Jason Krone for Comp150
'''

from collections import defaultdict
from math import exp, pow, log
import copy


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
        # the distortion constant
        self.alpha = float()


    ''' writes translations to the given file '''
    def write_translations_to_file(file_name):
        with open(file_name, 'w') as f:
            rows = list()
            for f in self.translations:
                for e in self.translations[f]:
                    prob = self.translations[f][e]
                    rows.append([f, e, prob])
            f.writerows(rows)


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
                print prob
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
                # add phrase pair ([e_start, e_end], [fs, fe]) to E
                e_phrase = ' '.join(e_sent[i] for i in xrange(e_start, e_end+1))
                f_phrase = ' '.join(f_sent[i] for i in xrange(fs, fe+1))
                if (fe-fs) <= MAX_PHRASE_LEN and (e_end-e_start) <= MAX_PHRASE_LEN:
                    E.add(((e_start, e_end+1), e_phrase, f_phrase))
                fe += 1
                if fe in f_aligned or fe == f_len:
                    break
            fs -= 1
            if fs in f_aligned or fs < 0:
                break
        return E


def alignment_from_line(line, src_is_english):
    cur_word_idx = 0
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


''' returns the alignment and target corpus for the given alignment file'''
def alignment_trg_corp(align_file, src_is_english):
    corpus = list()
    alignments = list()
    with open(e2f_file, 'r') as f:
        lines = f.readlines        
        for i, line in enumerate(lines):
            # target sentence line
            if i % 3 == 1: 
                sent = ['NULL'] + line.split()
                corpus.append(sent)
            # alignment line
            elif i % 3 == 2:
                alignments.append(alignment_from_line(line, src_is_english))
    return alignments, corpus


''' creates an instance of Symmetrizer using the given alignment files '''
def symetrizer_from_alignment_files(e2f_file, f2e_file):
    e2f, f_corpus = alignment_trg_corp(e2f_file, True)
    f2e, e_corpus = alignment_trg_corp(f2e_file, False)
    return Symmetrizer(e2f, f2e, e_corpus, f_corpus)
 

def main():
    # read in the first 100 tokenized sentences
    # e_corp = readlines.split()
    # f_corp = readlines.split()
    # e2f alignments
    # f2e alignments

main()
