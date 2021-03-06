from question_processing.target_extraction import get_target
from SPARQLWrapper import SPARQLWrapper, JSON
from sparqlquery import *
import socket

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

def check_internet():
    REMOTE_SERVER = "www.google.com"
    try:
        host = socket.gethostbyname(REMOTE_SERVER)
        s = socket.create_connection((host, 80), 2)
        return True
    except:
        return False

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
    conn=False
    conn=check_internet()
    if conn:
        answer = get_answer(question)
        if answer=="":
            with open("LOG/not_answered.txt", "a") as myfile:
                myfile.write(question)
            answer="Answer not found in DBpedia"
        else:
            with open("LOG/answered.txt", "a") as myfile:
                myfile.write(question)
        print "\nANS : ",answer
    else :
        answer = "ERROR :: Internet connection is not available..!!!"
    return answer
