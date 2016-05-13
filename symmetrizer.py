''' symmetrizer.py by Jason Krone for Comp150
'''

from collections import defaultdict
from math import exp, pow, log
import copy

class Symmetrizer(object):

    # TODO: must parse files and put in e2f , f2e format
    # these can be an array of sets of alignments
    # change alignments to be 0 indexed and fit string indicies
    # fcorpus and ecorpus just list of sentences of toks
    def __init__(self, e2f, f2e, f_corpus, e_corpus):
        self._e2f = e2f
        self._f2e = f2e
        self._fcorp = f_corpus
        self._ecorp = e_corpus
        # phrase_translations[englist_phrase][foreign_phrase] = log_prob
        self.phrase_translations = defaultdict((lambda : defaultdict(lambda : float('-inf'))))
        # the distortion constant
        self.alpha = float()


    ''' fills the phrase translation table using e2f and f2e alignments'''
    def symmetrize(self):
        phrase_pairs = set()
        zp = zip(self._e2f, self._f2e, self._ecorp, self._fcorp)

        # loop through sentence alignements and sentences
        for (e2f_align, f2e_align, e_sent, f_sent) in zp:
            dim = (len(e_sent), len(f_sent))
            alignment = self._grow_diag_final(e2f_align, f2e_align, dim)
            phrase_pairs.update(self._extract_phrase_pairs(alignment, e_sent, f_sent))

        # fill phrase_translations (probably using regex).
        # phi(t|s) = count(s, t) / count(s)
        # note: can potentially imporve scoring by smoothing
        # may want to prune the phrase table i.e. remove some phrase pairs
        # limit translation options for each phrase (often 20-30)
        # (just grab the 20 most probably once filled and re-normalize)
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
        bp = set()
        e_len, f_len = len(e_sent), len(f_sent)

        for e_start in xrange(e_len):
            for e_end in xrange(e_start, e_len):
                # find the minimally matching foreign phrase
                f_start, f_end = f_len-1, -1
                for (e, f) in A:
                    if e_start <= e <= e_end:
                        f_start = min(f, f_start)
                        f_end   = max(f, f_end)
                bp.update(self._extract(A, e_sent, f_sent , e_start, e_end, f_start, f_end))
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
                E.add(((e_start, e_end+1), e_phrase, f_phrase))
                fe += 1
                if fe in f_aligned or fe == f_len:
                    break
            fs -= 1
            if fs in f_aligned or fs < 0:
                break
        return E

def main():
    # read in the first 100 tokenized sentences
    # e_corp = readlines.split()
    # f_corp = readlines.split()
    # e2f alignments
    # f2e alignments

    trgtext = 'maria no dio una bofetada a la bruja verde'.split()
    srctext = 'mary did not slap the green witch'.split()

    e2f_align = set([(0, 0), (1, 5), (2, 1), (3, 2), (3, 3), (3, 4), (4, 6), (5, 8), (6, 7)])
    f2e_align = set([(0, 0), (1, 1), (2, 1), (3, 4), (4, 6), (5, 8), (6, 7)])

    sym = Symmetrizer(None, None, None, None)
    dim = (len(srctext), len(trgtext))
    A = sym._grow_diag_final(e2f_align, f2e_align, dim)
    phrases = sym._extract_phrase_pairs(A, srctext, trgtext)

    dlist = {}
    for p, a, b in phrases:
        if a in dlist:
            dlist[a][1].append(b)
        else:
            dlist[a] = [p, [b]]

    # Sort the list of translations based on their length.  Shorter phrases first.
    for v in dlist.values():
        v[1].sort(key=lambda x: len(x))

    # Function to help sort according to book example.
    def ordering(p):
        k,v = p
        return v[0]

    for i, p in enumerate(sorted(dlist.items(), key = ordering), 1):
        k, v = p
        print '({0:2}) {1} {2} - {3}'.format(i, v[0], k, ' ; '.join(v[1]))

main()
