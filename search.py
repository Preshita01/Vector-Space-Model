#!/usr/bin/python3
import re
import sys
import getopt
import ast
import os
import math
from index_helpers import tokenize
from search_helpers import *

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    
    # Step 1: Setting up the dictionaries
    final_terms = dict() # Setting up the dictionary containing all the terms from the corpus 
    normalized_lengths = dict() # Setting up the dictionary containing the normalized lengths of all the documents in the corpus

    with open(dict_file, 'r') as f:
        for line in f.readlines():

            if (line == "\n"): # If there is no valid query
                final_result = []
                write_results(final_result, results_file)
                continue

            term_and_info = line.split(': ')
            term = str(term_and_info[0])
            info = ast.literal_eval(term_and_info[1][:-1])

            if (type(info) == float): # If it the normalized length of a doc, add it to the normalized_lengths dict
                doc = term
                length = info
                normalized_lengths[doc] = length
            else:
                final_terms[term] = info

    # Resetting the results_file
    if (os.path.exists(results_file)):
        os.remove(results_file)

    # Starting to process queries
    queries = open(queries_file, 'r')

    for query in queries.readlines():
        # Step 2: Begin tokenizing the query (same precedure as in the indexing phase)
        search_terms_and_freq = tokenize(query)
        search_terms = list(search_terms_and_freq.items()) # Converting dictionary to a list
        
        # Step 3: Performing lnc.ltc
        total_num_of_docs = len(normalized_lengths)
        query_weights = ltc(search_terms, final_terms, total_num_of_docs) # Contains the weight for each term in the query
        
        # The key refers to the document id and the value is an array containing the weights for each search term
        docs_weights = lnc(search_terms, final_terms, postings_file)
        
        # Step 4: Go through all the documents, calculating the cosine similarities and extract the top 10 documents
        result = []
        
        # Calculating the normalization length for the query
        query_cos_normalization = 0
        for weight in query_weights:
            query_cos_normalization += weight**2
        query_cos_normalization = math.sqrt(query_cos_normalization)

        # Calculating the cosine similarities for the query and each document that contains at least 1 search term
        for doc in docs_weights:
            cos_similarity = 0

            for index in range(0, len(query_weights)):
                cos_similarity += query_weights[index] * docs_weights[doc][index]
           
            # Cosine normalize
            if (query_cos_normalization != 0): # Ensures a valid denominator
                cos_similarity = float(cos_similarity / query_cos_normalization) # Cosine normalize the weights
            
            doc_cos_normalization = normalized_lengths[doc] # Obtaining the normalized length for this specific document
            if (doc_cos_normalization != 0): # Ensures a valid denominator
                cos_similarity = float(cos_similarity / doc_cos_normalization) # Cosine normalize the weights 

            if (cos_similarity == 0): # Document is irrelevant
                continue
            
            # Checking if this document can be part of the top 10 documents to be returned
            pointer = 0
            
           # Traversing through the result list to see if the current document could be in the top 10
            while (pointer < len(result)):
                if (result[pointer][1] < cos_similarity):
                    break
                elif (result[pointer][1] == cos_similarity and int(result[pointer][0]) > int(doc)):
                    break
                else:
                    pointer += 1
            
            if (pointer < 10): # Add to the top 10 documents
                result.insert(pointer, (doc, cos_similarity))
            if (len(result) > 10):
                result.pop(-1) # Pop off the last element
        
        # Step 5: Output the top 10 documents
        write_results(result, results_file)


dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
