from question_processing.target_extraction import get_target
from SPARQLWrapper import SPARQLWrapper, JSON
from sparqlquery import *

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

def get_answer(question):
    coarse_class,fine_class,target,special_words = get_target(question)
    if coarse_class == 'HUM':
        from HUM import get_query
    elif coarse_class == 'ENTY':
        from ENTY import get_query
    elif coarse_class == 'DESC':
        from DESC import get_query
    elif coarse_class == 'NUM':
        from NUM import get_query
    elif coarse_class == 'LOC':
        from LOC import get_query
    elif coarse_class == 'ABBR':
        from ABBR import get_query
    else:
        print "Query not generated."


    return get_query(fine_class,target,special_words)

""" End of def get_answer """

def get_answer_UI(question):
    answer = get_answer(question)
    #print "\nANSER type : ",type(answer)
    return answer

""" #testing
q = "How many species of great white shark are there ?"
print "Q. ",q
answer = get_answer_UI(q)
print "\nAns : ",answer
"""
