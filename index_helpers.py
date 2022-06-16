import ast
import nltk
import math
import os
from nltk.stem.porter import *
"""
Contains all the helper functions for indexing
"""
def tokenize(lines):
    """
    Tokenizes the given file for indexing
    """
    # Contains the terms found in a specific file and its frequency in the specific file
    terms_and_freq = dict()

    sentences = nltk.sent_tokenize(lines, language='english')

    for sentence in sentences:
        words = nltk.word_tokenize(sentence, language='english', preserve_line=False)

        stemmer = PorterStemmer()

        for word in words:
            term = stemmer.stem(word) # Stemming
            new_term = term.lower() # Case-folding

            if (new_term in terms_and_freq):
                terms_and_freq[new_term] = terms_and_freq[new_term] + 1  # Increase the term frequency
            else:
                terms_and_freq[new_term] = 1 # Term currently has a term frequency of 1
    
    return terms_and_freq


def write_out_dicts_and_postings(in_mem_dict, out_dict, out_postings, lengths_dict):
    """
    Writes out the final dictionary and posting lists to the hard disk
    """
    # Resetting the out_dict and out_postings files
    if (os.path.exists(out_dict)):
        os.remove(out_dict)

    if (os.path.exists(out_postings)):
        os.remove(out_postings)
   
   # Tracks the starting position of the posting list pointers for the terms in the dictionary
    location = 0
    
    for term in in_mem_dict:
        curr_posting_list = in_mem_dict[term]
        curr_doc_freq = len(curr_posting_list)

        # Write the term, its document frequency and the pointer to its posting list to out_dict
        with open(out_dict, 'a+') as f:
            pointer = location
            f.write("%s: %s\n" % (term, [curr_doc_freq, pointer]))

        # Write the final posting list to out_postings
        with open(out_postings, 'a+') as f:
            string = ('%s\n' % curr_posting_list)
            f.write(string)
            location += len(string.encode('utf-8'))

    for doc_num in lengths_dict:
        normalized_length = lengths_dict[doc_num]

        with open(out_dict, 'a+') as f:
            f.write("%s: %s\n" % (doc_num, normalized_length))

