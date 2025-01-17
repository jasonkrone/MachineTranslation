# Beam Search (for Machine Translation)

# COMP 150: Natural Language Processing
# Jason Krone & Nicholas Yan
# 5/11/16

##################################################################################################
#                                                                                                #
#                                          ALGORITHM SKETCH                                      #
#                                                                                                #
##################################################################################################

""" 

The following code has been implemented utilizing the framework established by Daniel Jurafsky in
his textbook "Speech and Language Processing." 

The initial pseudocode presented by Jurafsky for a simple beam search appears below:

function BEAM_SEARCH_STACK_DECODER(source sentence) returns target_sentence

    initialize hypothesisStack[0 .. nf]
    push initial null hypothesis on hypothesisStack[0]
    for i in 0 to (nf - 1)
        for hyp in hypothesisStack[i]
            for new_hyp derived from hyp
                nf[new_hyp] = number of foreign words covered by new_hyp
                add new_hyp to hypothesisStack[nf[new_hyp]]
                prune hypothesisStack[nf[new_hyp]]
    find best hypothesis best_hyp in hypothesisStack[nf]
    return best path that leads to best_hyp via backtrace

Other helpful information on the algorithm behind beam search is available in:

    - the "Machine Translation" chapter in Jurafsky's text
    - "Pharaoh: A Beam Search Decoder for Phrase-Based Statistical Machine Translation Models" by 
      Philipp Koehn (http://homepages.inf.ed.ac.uk/pkoehn/publications/pharaoh-amta2004.pdf)

"""

##################################################################################################
#                                                                                                #
#                                            BEAM SEARCH                                         #
#                                                                                                #
##################################################################################################

import sys
import collections
import copy
from math import log, pow
from bigram import BigramLM

# enums for pruning methods
class Prune(object):
    THRESHOLD = 1
    HISTOGRAM = 2

# custom exception if there are no available transitions between two tokens
# (used when we are employing Viterbi)
class UnknownTransitionError(ValueError): pass

class BeamSearch: 

    # init
    #
    # args:     translation_table   dict, takes a first key (the word) and return a list of
    #                               all possible translations for that first key
    #           prune               the pruning method (THRESHOLD or HISTOGRAM)
    #           pthresh             the pruning threshold

    def __init__(self, training_set, translation_table, 
                 prune=Prune.HISTOGRAM, pthresh=5):

        self.all_translations = translation_table
        
        # populate the language model using the training_set
        self.transitions = self.create_bigram_lm(training_set)
        
        # set the beam search's pruning settings
        self.prune        = prune
        self.pthresh      = pthresh

    # create_bigram_lm
    #
    # args:     training_set        a training set (English) with which to construct the LM
    # 
    # returns:  returns a language model for English, trained on the training set, as well as
    #           a weight for unigrams and bigrams, assessed through deleted interpolation

    def create_bigram_lm (self, training_set):

        model = BigramLM()
        model.EstimateBigrams(training_set) 
        return model

    # transition_prob
    #
    # args:     prev_word           the first word in the word pair
    #           word                the second word in the word pair
    # 
    # returns:  returns the probability of the second word given the first, using simple
    #           linear interpolation for smoothing

    def transition_prob (self, prev_word, word):

        return self.transitions.LogProb_Laplace(prev_word, word)        

    # relevant_translations
    #
    # args:     source_sent         the foreign language sentence (to translate)
    #           translation_table   dict, takes a first key (the word) and return a list of
    #                               all possible translations for that first key (determined from
    #                               the training set)
    #
    # returns:  a dict in the same format of translation_table, but only with the phrases in
    #           source_sent

    def relevant_translations(self, source_sent):

        translations = collections.defaultdict(lambda: collections.defaultdict(float))

        # consider all possible combinations of phrases in the source sentence, adding them
        # to our translations table if a translation for that phrase has been seen before
        for (i, word) in enumerate(self.source_sent, start=0):
            
            curr_phrase = ""

            for j in range(i, self.num_words):

                if j is i:
                    curr_phrase = self.source_sent[j]
                else:
                    curr_phrase += " " + self.source_sent[j]

                if curr_phrase in self.all_translations:

                    for trans in self.all_translations[curr_phrase]:
                        translations[curr_phrase][trans] = self.all_translations[curr_phrase][trans]

        return translations

    # translate
    #
    # args:     source_sent     the source (foreign) sentence
    #
    # returns:  the hypothesis for best translated sentence

    def translate (self, source_sent):

        # convert all the words in the sentence to lowercase and add NULL to the beginning of 
        # the sentence
        source_sent = [word.lower() for word in source_sent]
        source_sent.insert(0, "NULL")

        # populate the source-sentence-dependent class elements
        self.source_sent  = source_sent
        self.num_words    = len(source_sent)
        # self.hyp_stacks   = [[]] * self.num_words
        self.hyp_stacks = [[] for _ in range(self.num_words + 1)]
        self.translations = self.relevant_translations(source_sent)

        # Tuple structure for candidates (that populate hypothesis stacks):
        #
        #   [0] new translated phrase
        #   [1] [0] original foreign word(s)
        #       [1] start index of the translated phrase
        #   [2] [0] marked words (list of booleans)
        #       [1] number of marked words
        #   [3] score
        #   [4] backpointer

        null_trans = None
        null_orig  = (None, None)
        null_marks = ([False] * self.num_words, 0)
        null_score = None
        null_bkptr = None
        null_cand  = (null_trans, null_orig, null_marks, null_score, null_bkptr) 

        self.hyp_stacks[0].append(null_cand)

        for i in range(0, self.num_words + 1):

            for (j, hyp) in enumerate(self.hyp_stacks[i], start=0):

                # tuple pointing to the current location of the candidate to expand
                # (to use as backpointer for expansions of the candidate)
                curr_loc = (i, j)

                for new_cand in self.expansions(hyp, curr_loc):

                    new_cand_len = new_cand[2][1]

                    self.hyp_stacks[new_cand_len] = self.insert_hyp(new_cand, 
                                                                    self.hyp_stacks[new_cand_len], 
                                                                    self.prune, self.pthresh)

        for i in range(self.num_words - 1, -1, -1):
            translation = self.backtrace(self.best_cand(self.hyp_stacks[i]))
            if translation != "No translation found.":
                return translation.split()

        return "No translation found."

    # expansions
    #
    # args:     hyp         the hypothesis to expand
    #           loc         a tuple containing the stack number and index within that stack for
    #                       the current hypothesis
    #           source      the source sentence          
    #
    # returns:  a list of possible new hypotheses

    def expansions (self, hyp, loc):

        exps = []

        # cand  =   [0] new translated phrase
        #           [1] [0] original foreign word(s)
        #               [1] start index (index of first orig. word in foreign sentence)
        #           [2] [0] marked words (list of booleans)
        #               [1] number of marked words
        #           [3] score
        #           [4] backpointer

        curr_word    = hyp[0]
        curr_foreign = hyp[1][0]
        curr_marked  = hyp[2][0]
        curr_len     = hyp[2][1]
        curr_score   = hyp[3]
        curr_loc     = loc           # the location of the current cand within the hyp_stacks

        for (index, word_slot) in enumerate(curr_marked, start=0):

            # the word in the index has already been translated previously
            if word_slot is True:
                continue

            # the word in the index still needs translation
            else:

                curr_phrase = ""

                # for all possible phrases starting with that word, if the phrase is in the 
                # translation table, create an expansion using the phrase

                for phrase_end in range(index, self.num_words):

                    if curr_marked[phrase_end] is True:
                        break

                    if phrase_end is index:
                        curr_phrase = self.source_sent[phrase_end]
                    else:
                        curr_phrase = curr_phrase + " " + self.source_sent[phrase_end]

                    if curr_phrase in self.translations:

                        for poss_trans in self.translations[curr_phrase]:
                            new_exp = self.create_expansion(poss_trans, index, phrase_end + 1,
                                                            curr_marked, curr_len, curr_score, curr_loc)
                            if new_exp is not None:
                                exps.append(new_exp)

        return exps

    # create_expansion
    #
    # args:    poss_trans    a translation of the given foreign phrase
    #          index         the starting index of the foreign phrase
    #          phrase_end    the ending index of the foreign phrase
    #          curr_marked   the hypothesis's currently translated set of words
    #          curr_len      "   "            number of currently translated words
    #          curr_score    "   "            score
    #          curr_loc      "   "            location within self.hyp_stacks
    #
    # returns: an entry to add to one of the hypothesis stacks encapsulating the given information;
    #          returns none in the event than no valid expansion can be created from the given
    #          information

    def create_expansion (self, poss_trans, index, phrase_end, 
                          curr_marked, curr_len, curr_score, curr_loc):

        exp_word    = poss_trans

        exp_foreign = ""
        for i in range(index, phrase_end):
            if i is index:
                exp_foreign = self.source_sent[i]
            else:
                exp_foreign = exp_foreign + " " + self.source_sent[i]

        exp_index   = (index, phrase_end)

        # while traversing through the marked array, ensure that none of the words in the phrase
        # have been previously translated
        exp_marked  = copy.deepcopy(curr_marked)
        for i in range(index, phrase_end):
            if exp_marked[i] is False:
                exp_marked[i] = True
            else:
                return None

        exp_len     = curr_len + (phrase_end - index)

        exp_bkptr   = curr_loc

        # in the cand passed to the score function, the score of the candidate is
        # left blank (this is the value to be calculated)
        exp_score  = self.score((exp_word, 
                                 (exp_foreign, exp_index),
                                 (exp_marked, exp_len), 
                                None,
                                exp_bkptr),
                                curr_score)

        return ((exp_word, 
                    (exp_foreign, exp_index),
                    (exp_marked, exp_len),
                    exp_score,
                    exp_bkptr))

    # insert_hyp
    # 
    # args:     hyp         the hypothesis to insert
    #           hypStack    the hypothesis stack to insert the hypothesis into
    #           prune       the pruning method (THRESHOLD or HISTOGRAM)
    #           pthresh     the pruning threshold
    #
    # returns:  the hypothesis stack, with the hyp added (if it meets the pruning threshold)
    #
    # notes:    hypStacks invariant: a hypothesis stack is always in sorted order (where index 0 has 
    #           the lowest priority)

    def insert_hyp (self, hyp, hypStack, prune, pthresh):

        hypStack.append(hyp)
        hypStack.sort(key=lambda tup: tup[3])

        # prune the stack as needed and return the new stack
        return self.prune_stack(hypStack, prune, pthresh)

    # score
    #
    # args:     hyp         the hypothesis to score
    #           prev_cost   the cost of the previous stage (backpointer) of the search
    #
    # returns:  the score of the given hypothesis    

    def score (self, hyp, prev_cost):

        return self.present_cost(hyp, prev_cost) + self.future_cost(hyp)

    # present_cost
    #
    # args:     hyp                 the hypothesis to score
    #           prev_cost           the cost of the previous stage (backpointer) of the search
    #
    # returns:  the present cost of the given hypothesis

    def present_cost (self, hyp, prev_cost):

        # cand  =   [0] new translated phrase
        #           [1] [0] original foreign word
        #               [1] translated index (index of orig. word in foreign sentence)
        #           [2] [0] marked words (list of booleans)
        #               [1] number of marked words
        #           [3] score
        #           [4] backpointer

        translated = hyp[0]
        foreign    = hyp[1][0]
        (prev_stack, stack_loc) = hyp[4]
        prev_word  = self.hyp_stacks[prev_stack][stack_loc][0]

        # present_cost formula from Jurafsky, p. 36 of "Machine Translation" chapter
        translation_p = self.translations[foreign][translated]

        # only take distortion and transition into account when there is valid previous word
        if prev_word is not None:
        
            distortion_p  = self.distortion(hyp)
            transition_p  = self.transition_prob(self.get_last_word(prev_word), 
                                                 self.get_first_word(translated))

            return prev_cost + translation_p + log(distortion_p) + transition_p

        else:

            return translation_p

    def get_first_word (self, phrase):
        return phrase.split(' ', 1)[0]

    def get_last_word (self, phrase):
        return phrase.split(' ', 1)[-1]

    # distortion
    # 
    # args:     hyp         the hypothesis to calculate the distortion of
    #           [alpha]     (OPTIONAL) default has been determined on the training set using
    #                       GIZA++, but the user can specify an alternative alpha value
    # returns: 

    def distortion (self, hyp, alpha=0.5):

        (curr_start, _) = hyp[1][1]
        
        (prev_stack, stack_loc) = hyp[4]
        prev_hyp        = self.hyp_stacks[prev_stack][stack_loc]
        (_, prev_end)   = prev_hyp[1][1]
        return pow(alpha, abs(curr_start - prev_end - 1))

    # future_cost
    #
    # args:     hyp         the hypothesis to score
    #
    # returns:  the future cost of the given hypothesis

    def future_cost (self, hyp):

        # gather still-to-be-translated words from the hypothesis
        # TODO : place for improvement (consider phrases)
        unmarked = []
        for (i, marked) in enumerate(hyp[2][0], start=0):
            if marked is False:
                unmarked.append(self.source_sent[i])

        # if all marked, no future cost
        if not unmarked:
            return 0.0

        # if there were no transitions between two words in the sentence
        # seen in our training set, return negative infinity as the probability
        try:
            v_probs = self.populate_viterbi_probs(unmarked)
        except UnknownTransitionError:
            return float("-inf")

        # else return the best log probability
        return self.best_viterbi_prob(v_probs)

    # populate_viterbi_probs
    # 
    # args:    sent     a given list of words to calculate the Viterbi probability table for
    # 
    # returns: the populated dynamic programming table of Viterbi (log) probabilities

    def populate_viterbi_probs(self, sent):

        v_probs = []

        for (i, word) in enumerate(sent, start=0):

            v_probs.append({})
            
            # initialize the first cell in the Viterbi probability table (base case in dynamic 
            # programming algorithm)
            if i == 0:

                for trans in self.translations[sent[i]]:
                    v_probs[i][trans] = self.translations[sent[i]][trans]

            # otherwise, populate the probability table with the highest probabilities of seeing 
            # the given translation at the current word, based on the previous possible 
            # translations
            else:

                for trans in self.translations[sent[i]]:

                    trans_prob = self.translations[sent[i]][trans]
                    best_prob  = None

                    for prev_trans in v_probs[i - 1]:
                        curr_prob = trans_prob * self.transition_prob(prev_trans, trans)

                        if best_prob is None or curr_prob > best_prob:
                            best_prob = curr_prob

                    if best_prob is not None:
                        v_probs[i][trans] = best_prob

                if len(v_probs[i]) is 0:
                    raise UnknownTransitionError

        return v_probs

    # best_viterbi_prob
    #
    # args:    vprobs   a table of Viterbi probabilities (generated via PopulateViterbiProbs)
    #
    # returns: the minimum Viterbi probability in the (last column of the) given table of Viterbi 
    #          probabilities

    def best_viterbi_prob(self, v_probs):

        num_cols = len(v_probs)
        best = float("-inf")

        for term in v_probs[num_cols - 1]:
            prob = v_probs[num_cols - 1][term]
            if prob > best:
                best = prob

        return best

    # prune_stack
    #
    # args:     hypStack    the hypothesis stack to prune
    #           prune       the pruning method (THRESHOLD or HISTOGRAM)
    #           pthresh     the pruning threshold
    #
    # returns:  a pruned version of the supplies hypStack, pruned using the given methods / threshold

    def prune_stack (self, hypStack, prune, pthresh):

        minScore = self.min_score(hypStack, prune, pthresh)

        # while the lowest entry in the hypStack is less than the minScore, continue dropping
        # entries from the stack
        while len(hypStack) > 0 and hypStack[0][3] < minScore:
            hypStack.pop(0)

        return hypStack

    # calc_thresh
    #
    # args:     hypStack    the hypothesis stack on which to calculate the min score
    #           prune       the pruning method (THRESHOLD or HISTOGRAM)
    #           pthresh     the pruning threshold
    #
    # returns:  the min score required to retain an entry in the given hypStack

    def min_score (self, hypStack, prune, pthresh):

        if prune is Prune.THRESHOLD:

            if len(hypStack) is 0:
                return float("-inf")

            # pthresh is the alpha value
            else:
                return pthresh * hypStack[-1][1]

        elif prune is Prune.HISTOGRAM:

            if len(hypStack) < pthresh:
                return float("-inf")

            # pthresh is the number of values to keep in the hypStack at once
            else:
                return hypStack[-pthresh][1]

        else:
            raise ValueError("Invalid pruning metric supplied.")

    # best_cand
    #
    # args:     hyp_stack   the hypothesis stack to search
    #
    # returns:  the best candidate within the given hypothesis stack

    def best_cand (self, hyp_stack):

        best = None

        for cand in hyp_stack:
            if best is None or cand[3] > best[3]:
                best = cand

        return best

    # backtrace
    #
    # args:     cand        the candidate whose path to backtrace
    #
    # returns:  the sentence with the candidate at the end

    def backtrace (self, cand):

        if cand is None:
            return "No translation found."

        curr_word  = cand[0]

        # base case: at the beginning of the sentence (no more to backtrace)
        if cand[4] is None:
            return ""

        # recursive case: append the current word onto the end of the remainder of the sentence
        # to backtrace
        else:

            (prev_stack, index) = cand[4]
            prev_cand  = self.hyp_stacks[prev_stack][index]
            prev_words = self.backtrace(prev_cand)

            # space-handling; don't prepend a space to the beginning of a sentence
            if prev_words == "":
                return curr_word
            else:
                return prev_words + " " + curr_word
