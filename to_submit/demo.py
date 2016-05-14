import sys
from beam_search import BeamSearch
from utilities import get_word_translations, tokenize, get_datasets
from direct_trans import DirectTrans

def main():

    english = tokenize("data/100ktok.low.en")
    spanish = tokenize("data/100ktok.low.es")

    training_set, test_set, translated_set = get_datasets(english, spanish)
    translations = get_word_translations("3000_trans.txt")

    print "Original Sentence:", ' '.join(test_set[0])

    translator = DirectTrans(translations)
    print "Direct Translation:", ' '.join(translator.translate(test_set[0]))

    test_output = open('trans_beam.txt','w')
    true_output = open('trans_true.txt','w')

    search = BeamSearch(training_set, translations)
    print "Beam Translation:", ' '.join(search.translate(test_set[0]))
    print "True Translation:", ' '.join(translated_set[0])

if __name__ == "__main__": 
    main()