import sys
import argparse
from collections import OrderedDict
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.corpus import wordnet

punctuation_marks = [",", ".", "...", ';', "'", "\"", ':', '?', "!", '|', '%', '$', '#', '@', '&', '*', '+', '-', '>', '<', '(', ')', '[', ']', '{', '}', '=']

def print_dictionary(fw, dictionary_of_distinct_words):
    for index in dictionary_of_distinct_words:
        fw.write(index + " " + str(dictionary_of_distinct_words[index]) + "\n")
        fw.flush()

def main():

    dictionary_of_distinct_words = OrderedDict()

    stemmer = PorterStemmer()
    lemmatiser = WordNetLemmatizer()

    parser = argparse.ArgumentParser(description=None)
    parser.add_argument("inputfile", help="Name of the file which contains 1 token per line")
    args = parser.parse_args()

    fr = open(args.inputfile, 'r')
    fw = open('output.txt', 'w')

    list_of_stopwords = stopwords.words('english')

    for token in fr:
        token = token.replace("\n", "").strip()

        if token.startswith("CF:D") or token.startswith("CF:T"):
            pass
        elif token in punctuation_marks or token in list_of_stopwords or token.isdigit():
            continue
        else:
            if  wordnet.synsets(token):
                token = lemmatiser.lemmatize(token, pos = wordnet.synsets(token)[0].pos())
            token = token.lower()

        if token in dictionary_of_distinct_words:
            dictionary_of_distinct_words[token] += 1
        else:
            dictionary_of_distinct_words[token] = 1

    print_dictionary(fw, dictionary_of_distinct_words)

if __name__ == '__main__':
    main()
