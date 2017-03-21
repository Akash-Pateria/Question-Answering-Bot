from question_processing.target_extraction import get_target
from sparqlquery import *

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


    get_query(fine_class,target,special_words)

""" End of def get_answer """
file_r=open("loc_data.txt","r")#/home/akash/juggernaut/classifier/FineOutputFiles/ABBR_training.txt","r")
for line in file_r:
    t=line.split(":")[-1]
    if t.split()[0]!="city":
        q=t.split(' ',1)[1]
        get_answer(q)
        print "================================================================================================="


#get_answer("What does CPR stand for ?")
