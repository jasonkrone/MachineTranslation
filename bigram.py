# Bigram Language Model (for Machine Translation)

# COMP 150: Natural Language Processing
# Jason Krone & Nicholas Yan
# 5/12/16

##################################################################################################
#                                                                                                #
#                                      BIGRAM LANGUAGE MODEL                                     #
#                                                                                                #
##################################################################################################

import sys
from collections import defaultdict
from math import log, exp

class BigramLM:

    def __init__(self):

        # unigram_counts[unigram] = count
        self.unigram_counts = defaultdict(float)
        self.total_unigrams = 0
        self.total_uq_unigrams = 0

        # bigram_counts[first_word][second_word] = count
        self.bigram_counts = defaultdict(lambda : defaultdict(float))
        self.total_bigrams = 0
        self.total_uq_bigrams = 0

        # log_probsfirst_word][second_word] = log_probability
        self.log_probs = defaultdict(lambda : defaultdict(float))

    # EstimateBigrams
    #
    # args:     train_corpus    the training corpus to model
    #
    # returns:  none; populates the model's log probability table with the log probability of each #           phrase in the train_corpus

    def EstimateBigrams(self, train_corpus):

        self.LoadNGrams(train_corpus)
        self.CalcLogProbs()

    # LoadNGrams
    #
    # args:     train_corpus    the training corpus to model
    #
    # returns:  none; populates the model's unigram count and bigram count tables based on the
    #           number of instances of each unigram and bigram within the train_corpus

    def LoadNGrams(self, train_corpus):

        for sentence in train_corpus:

            prev_word = ''
            for word in sentence:

                # load the unigram
                self.AddUnigram(word)

                # load the bigram
                if prev_word is not '':
                    self.AddBigram(prev_word, word)
                    
                prev_word = word

    # AddUnigram
    #
    # args:     word        a unigram
    #
    # returns:  none; adds a unigram and increments its count within the model's unigram count
    #           table (if a unigram has not been seen before, its count is 1)

    def AddUnigram(self, word):
        
        # increment the total count of all unigrams
        self.total_unigrams = self.total_unigrams + 1

        # if we haven't seen the current unigram before, increment the total
        # count of unique unigrams
        if word not in self.unigram_counts:
            self.total_uq_unigrams = self.total_uq_unigrams + 1

        self.unigram_counts[word] = self.unigram_counts[word] + 1
        
    # AddBigram
    #
    # args:     word        a bigram
    #
    # returns:  none; adds a bigram and increments its count within the model's bigram count
    #           table (if a bigram has not been seen before, its count is 1)

    def AddBigram(self, word1, word2):

        # increment the toal count of all bigrams
        self.total_bigrams = self.total_bigrams + 1
        
        # if we haven't seen the current bigram before, increment the total
        # count of unique bigrams
        if word2 not in self.bigram_counts[word1]:
            self.total_uq_bigrams = self.total_uq_bigrams + 1

        self.bigram_counts[word1][word2] = self.bigram_counts[word1][word2] + 1

    # CalcLogProbs
    #
    # args:     none
    #
    # returns:  none; called to normalize the bigram count table, populating the log probability
    #           table stored in the class

    def CalcLogProbs(self):

        for unigram in self.unigram_counts:

            # for the current word:
            # - curr_uq_successors: number of unique successors
            # - curr_total_successors: total number of successors
            curr_uq_successors = self.bigram_counts[unigram]
            curr_total_successors = sum(curr_uq_successors.values())

            for successor in curr_uq_successors:

                successor_freq = curr_uq_successors[successor]

                p_bigram = successor_freq / curr_total_successors
                self.log_probs[unigram][successor] = log(p_bigram)

    # CalcLogProbs
    #
    # args:     none
    #
    # returns:  checks the distribution of the log probability table, ensuring that the 
    #           total probability of each bigram, given the first word, is 1

    def CheckDistribution(self):

        for unigram in self.unigram_counts:

            if unigram is end_token:
                continue

            total_prob = sum(exp(x) for x in self.log_probs[unigram].values())
            assert numpy.isclose(total_prob, 1)

    # LogProb_NoSmooth
    #
    # args:     prev_word           the first word in the word pair
    #           word                the second word in the word pair
    # 
    # returns:  given a bigram (composed of prev_word and word), returns the log probability of 
    #           that bigram - without any smoothing

    def LogProb_NoSmooth(self, prev_word, word):

        if word in self.log_probs[prev_word]:
            return self.log_probs[prev_word][word]
        else:
            raise UnknownBigramError

    # LogProb_Laplace
    #
    # args:     prev_word           the first word in the word pair
    #           word                the second word in the word pair
    # 
    # returns:  given a bigram (composed of prev_word and word), returns the log probability of 
    #           that bigram - with Laplace smoothing

    def LogProb_Laplace(self, prev_word, word):

        N = sum(self.bigram_counts[prev_word].values())
        V = self.total_uq_unigrams - 1

        # if we've seen this bigram before...
        if word in self.bigram_counts[prev_word]:

            return log((self.bigram_counts[prev_word][word] + 1.0) /
                       (N + V))

        # if we haven't seen this bigram before...
        else:
            return log(1.0 / (N + V))

    # LogProb_SimpleInterp
    #
    # args:     prev_word           the first word in the word pair
    #           word                the second word in the word pair
    #           w_unigram           the unigram weight to utilize in the simple linear 
    #                               interpolation calculation
    #           w_bigram            similar to w_unigram, but for bigram weight
    # 
    # returns:  given a bigram (composed of prev_word and word), returns the log probability of 
    #           that bigram - using simple linear interpolation to calculate the base probability

    def LogProb_SimpleInterp(self, prev_word, word, w_unigram, w_bigram):

        successor_freq = None
        curr_total_successors = None
        p_bigram = None

        # try to find the count of the pre-exsiting bigram; if there is none,
        # the probability of the given bigram is 0
        if word in self.bigram_counts[prev_word]:

            successor_freq = self.bigram_counts[prev_word][word]
            curr_total_successors = sum(self.bigram_counts[prev_word].values())        
            p_bigram = successor_freq / curr_total_successors
        
        else:
            p_bigram = 0

        p_unigram = self.unigram_counts[word] / self.total_unigrams

        return log(w_unigram * p_unigram + w_bigram * p_bigram)

    # ApplyDeletedInterp
    #
    # args:     held_out_corpus         a held out dataset (distinct from train and test sets)
    # 
    # returns:  returns the best unigram and bigram weights to utilize (in simple linear
    #           interpolation), based on the language model constructed of the held out corpus
    #
    # notes:    algorithm based on outlined available in Speech and Language Processing by
    #           Daniel Jurafsky

    def ApplyDeletedInterp(self, held_out_corpus):

        w_unigram = 0.0
        w_bigram = 0.0

        for first_word in self.bigram_counts:

            for second_word in self.bigram_counts[first_word]:

                num_bigram_matches = self.bigram_counts[first_word][second_word]

                # if the denominator of a case is zero, assume that the
                # value of the case is zero
                try: 
                    case_bigram = (num_bigram_matches - 1) / \
                                  (self.unigram_counts[first_word] - 1)
                except ZeroDivisionError:
                    case_bigram = 0

                try:
                    case_unigram = (self.unigram_counts[second_word] - 1) / \
                                   (self.total_unigrams - 1)
                except ZeroDivisionError:
                    case_unigram = 0

                if max(case_bigram, case_unigram) is case_bigram:
                    w_bigram = w_bigram + num_bigram_matches
                else:
                    w_unigram = w_unigram + num_bigram_matches

        w_total = w_unigram + w_bigram

        return (w_unigram / w_total), (w_bigram / w_total)