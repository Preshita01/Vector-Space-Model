import ast
import nltk
from nltk.stem.porter import *
import math

"""
Includes all the helper functions required to soleve the free text search queries
"""
def get_posting_list(term, dictionary, postings_file):
    """
    Retrieves the relevant posting list
    """
    posting_list = []

    if (term in dictionary): # If term exits
        with open(postings_file, 'r') as f:
            term_list_pt = dictionary[term][1]
            f.seek(term_list_pt)
            posting_list = ast.literal_eval(f.readline())
            f.seek(0) # Reset 
    
    # Return posting_list
    return posting_list


def ltc(search_terms, final_terms, total_num_of_docs):
    """
    Executing the weighting scheme for a query
    """
    query_weights = [] # Contains the weight for each term in the query
    
    for index in range(0, len(search_terms)):
        # Processing for query
        curr_term = search_terms[index][0]
        curr_query_term_freq = search_terms[index][1]

        # Calculating log(tf)
        log_query_term_freq = 0
        if (curr_query_term_freq > 0): # Ensures that the log function produces a valid output
            log_query_term_freq = 1 + math.log(curr_query_term_freq, 10)

        # Calculating idf
        curr_doc_freq = 0
        if (curr_term in final_terms): # If the term was found
            curr_doc_freq = final_terms[curr_term][0]

        query_idf = 0
        
        # Ensures that the log function produces a valid output
        if (curr_doc_freq != 0 and float(total_num_of_docs / curr_doc_freq) > 0):
            query_idf = math.log(float(total_num_of_docs / curr_doc_freq), 10)

        # Calculating tf-idf
        query_weight = log_query_term_freq * query_idf
        query_weights.append(query_weight) # Yet to be normalised
    
    # Returning the list of query weights
    return query_weights


def lnc(search_terms, final_terms, postings_file):
    """
    Executing the weighting scheme for every document that contains at least 1 search term
    """
    docs_weights = dict()

    for index in range(0, len(search_terms)):
        curr_term = search_terms[index][0]

        # Processing for all documents that contain at least 1 of the search terms
        posting_list = get_posting_list(curr_term, final_terms, postings_file)
        
        for doc in posting_list: # If term doesn't exist in final_terms, doc_weights will remain empty
            doc_num = doc[0]
            curr_doc_term_freq = doc[1]

            # Calculating log(tf)
            log_doc_term_freq = 0
            if (curr_doc_term_freq > 0): # Ensures that the log function produces a valid output
                log_doc_term_freq = 1 + math.log(curr_doc_term_freq, 10)

            doc_weight = log_doc_term_freq

            if (doc_num not in docs_weights):
                docs_weights[doc_num] = []
            
            # Initialising the array with a 0 for each search term. The weights for the individual search terms 
            # may then be updated to non-zero values. (Each position in the array corresponds to a specific search term)
            for i in range(0, len(search_terms)):
                docs_weights[doc_num].append(0)
            
            docs_weights[doc_num][index] = doc_weight # Append the latest doc_weight
    
    # Return the dictionary of docs and weights
    return docs_weights


def write_results(result, results_file):
    """
    Writes the final results to the output file
    """
    with open(results_file, 'a+') as f:
        for index in range(0, len(result)):
            if (index == len(result) - 1):
                f.write("%s" % result[index][0])
            else:
                f.write("%s " % result[index][0])
        f.write("\n")

