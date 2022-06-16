#!/usr/bin/python3
import re
import sys
import getopt
import math
import os
from index_helpers import *
from os import listdir

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

def build_index(in_dir, out_dict, out_postings):
    """
    build index from documents stored in the input directory,
    then output the dictionary file and postings file
    """
    print('indexing...')
    
    # Final dictionary containing all terms and their respective posting lists in memory at all times
    final_dict = dict()

    # Dictionary containing the normalized lengths for each document
    normalized_lengths = dict()

    # Variable tracking the sum of the squares of the individual terms in a document
    doc_length = 0

    # Step 1: Indexing
    for in_file in listdir(in_dir):
        
        # Start indexing current file
        text_file = open(in_dir + in_file, 'r')
        lines = text_file.read()
            
        # Begin tokenizing
        terms_and_freq = tokenize(lines) # Contains the terms found in a specific file and its frequency in the specific file
        
        # For every term in the current file
        for curr_term in terms_and_freq:
            if (terms_and_freq[curr_term] > 0):
                doc_length += (1 + math.log(terms_and_freq[curr_term], 10))**2
            
            if (curr_term in final_dict):
                # Add the ID of this new document to the posting list
                final_dict[curr_term].append((in_file, terms_and_freq[curr_term])) # Appending the tuple (doc_id, term_freq)
            else:
                # Create a posting list for this new term
                final_dict[curr_term] = [(in_file, terms_and_freq[curr_term])] # Newly adding the tuple (doc_id, term_freq)
        
        # Recording the normalized length of the current file
        normalized_lengths[in_file] = math.sqrt(doc_length)

        text_file.close()

        # Reset file-based variables
        doc_length = 0
    
    # Step 2: Writing out posting lists to the hard disk
    print("writing out the posting lists now...")
    write_out_dicts_and_postings(final_dict, out_dict, out_postings, normalized_lengths)


input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"

if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)

build_index(input_directory, output_file_dictionary, output_file_postings)
