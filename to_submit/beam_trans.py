import sys
from beam_search import BeamSearch
from utilities import get_word_translations, tokenize, get_datasets

def main():

    english = tokenize("data/100ktok.low.en")
    spanish = tokenize("data/100ktok.low.es")

    training_set, test_set, translated_set = get_datasets(english, spanish)
    translations = get_word_translations("3000_trans.txt")
    search = BeamSearch(training_set, translations)

    test_output = open('trans_beam.txt','w')
    true_output = open('trans_true.txt','w')

    for i in range(len(test_set)):
        print "Translating sentence", i, "..."
        test_output.write(' '.join(search.translate(test_set[i])) + "\n")
        true_output.write(' '.join(translated_set[i]) + "\n")

    test_output.close()
    true_output.close()

if __name__ == "__main__": 
    main()