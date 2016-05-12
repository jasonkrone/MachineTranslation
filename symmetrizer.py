''' symmetrizer.py by Jason Krone for Comp150
'''

from collections import defaultdict
from math import exp, pow, log

class Symmetrizer(object):

    # TODO: must parse files and put in e2f , f2e format
    # these can be an array of sets of alignments
    # change alignments to be 0 indexed and fit string indicies
    def __init__(e2f, f2e, fcorpus, ecorpus):
        self._e2f = e2f
        self._f2e = f2e
        self._fcorp = fcorp
        self._ecorp = ecorp
        # phrase_translations[englist_phrase][foreign_phrase] = log_prob
        self.phrase_translations = defaultdict(defaultdict(lambda : float("-inf")))
        # the distortion constant
        self.alpha = float()


    ''' fills the phrase translation table using e2f and f2e alignments'''
    def symmetrize(self):
        phrase_pairs = set()
        zp = zip(self._e2f, self._f2e, self._ecorp, self._fcorp)
        # loop through sentence alignements and sentences
        for (e2f_align, f2e_align, e_sent, f_sent) in zp:
            alignment = self._grow_diag_final(e2f_align, f2e_align)
            phrase_pairs.union(self._extract_phrase_pairs(alignment, e_sent, f_sent))

        # fill phrase_translations (probably using regex).
        # phi(t|s) = count(s, t) / count(s)
        # note: can potentially imporve scoring by smoothing
        # may want to prune the phrase table i.e. remove some phrase pairs
        # limit translation options for each phrase (often 20-30)
        # (just grab the 20 most probably once filled and re-normalize)
        # can use chi squared stats based pruning (prob not this)


    ''' ues grow-diag-final to create a alignment between e2f and f2e '''
    def _grow_diag_final(self, e2f_align, f2e_align):
        intersect = e2f_align.intersection(f2e_align)
        union     = e2f_align.union(f2e_align)
        alignment = self._grow_diag(intersect, union)
        alignment = final(e2f_align, alignment)
        alignment = final(f2e_align, alignment)
        return alignment


    def _extract_phrase_pairs(self, alignment, esent, fsent):
        # will need to use self._fcorp and self._ecorp to get the aligns


    ############# HELPER FUNCTIONS FOR GROW-DIAG-FINAL ##############


    ''' grows the alignment by selectively adding elems from union '''
    def _grow_diag(self, alignment, union):
        points_added = True
        while points_added:
            points_added = False
            for aligned_pair in alignment:
                for (e_new, f_new) in self._neighbors(aligned_pair):
                    # e-new not aligned or f-new not aligned
                    aligns = [(x, y) for x, y in alignment if x == e_new or y == f_new]
                    if len(aligns) == 0 and (e_new, f_new) in union:
                        alignment.union((e_new, f_new))
                        points_added = True
        return alignment


    ''' returns list of possible neighboring alignments '''
    def _neighbors(self, aligned_pair):
        neighboring = [(-1,0),(0,-1),(1,0),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        x, y = aligned_pair
        points = [(x + s, y + t) for s, t in neighboring]
        return filter(points, lambda p : p[0] >= 0 and p[1] >= 0)


    ''' adds select points from a to alignment '''
    def _final(a, alignment):
        # words aligned in a
        for (e_new, f_new) in a:
            aligns = [(x, y) for x, y in alignment if x == e_new or y == f_new]
            if len(aligns) == 0:
                alignment.union((e_new, f_new))
        return alignment
