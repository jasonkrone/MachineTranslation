''' symmetrizer.py by Jason Krone for Comp150
'''

from collections import defaultdict
from math import exp, pow, log

class Symmetrizer(object):

    def __init__(e2f, f2e, fcorpus, ecorpus):
        self._e2f = e2f
        self._f2e = f2e
        self._fcorpus = fcorpus
        self._ecorpus = ecorpus
        # phrase_translations[englist_phrase][foreign_phrase] = log_prob
        self.phrase_translations = defaultdict(defaultdict(lambda : float("-inf")))
        # the distortion constant
        self.alpha = float()

    ''' fills the phrase translation table using e2f and f2e '''
    def symmetrize(self):
        phrase_pairs = set()
        zp = zip(self._fcorpus, self._ecorpus)
        for (f_sent, e_sent) in zp:
            alignment = self._grow_diag_final(e_sent, f_sent)
            phrase_pairs.union(self._extract_phrase_pairs(alignment))

        # fill phrase_translations (probably using regex).
        # phi(t|s) = count(s, t) / count(s)
        # note: can potentially imporve scoring by smoothing
        # may want to prune the phrase table i.e. remove some phrase pairs
        # limit translation options for each phrase (often 20-30)
        # (just grab the 20 most probably once filled and re-normalize)
        # can use chi squared stats based pruning (prob not this)


    ''' uses MLE to compute the best alignment for the given sentance '''
    def _alignment_for_sent(self, src_sent, trg_sent, word_alignments):
        # TODO: figure out how to do word alignment for sentanaces
        # might just do all word alignments that match
        # i.e. trg(word) is in the sentance and then mark that as a poss
        # i think that is right

    def _extract_phrase_pairs(self, alignment):


    ################# FUNCTIONS FOR ALIGNMENT ####################


    ''' ues grow-diag-final to create a alignment between e2f and f2e '''
    def _grow_diag_final(self, e_sent, f_sent):
        e_align = self._alignment_for_sent(e_sent, f_sent, self._e2f)
        f_align = self._alignment_for_sent(f_sent, e_sent, self._f2e)
        # TODO: may need to index e and f
        intersect = self._intersect(e_align, f_align)
        union     = self._union(e_align, f_align)
        self._grow_diag(intersect, union)
        final(e_alignment)
        final(f_alignment)

    ''' grows the alignment by selectively adding elems from union '''
    def _grow_diag(self, alignment, union):
        points_added = True
        while points_added:
            points_added = False
            # for each aligned pair (e_i, f_i)
            for e, f in alignment.items():
                # for each neighboring point (e-new, f-new)
                    # if e-new is not aligned or f-new not aligned
                    # and (e-new, f-new) in union
                        # add (e-new, f-new) to alignment
                        points_added = True
        return alignment

    ''' adds select points from a to alignment '''
    def _final(a, alignment):
        # words aligned in a
        for e-new, f-new in a:
            # if e-new not aligned in align or f-new not aligned in align
                # add (e-new, f-new) to alignment
        return alignment


    ''' returns the intersection of the two alignments '''
    def _intersect(self, e_align, f_align):
        # could do dictionaries for e_align and f_align
        # that map english -> foreign
        # then convert those into items
        # make a set from items
        # then make a dictionary again from that set
        # return the dictionary

    def _union(self, e_align, f_align):
        # copy data struct used above

