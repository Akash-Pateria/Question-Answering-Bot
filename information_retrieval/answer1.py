from question_processing.target_extraction import get_target
from sparqlquery import *

<<<<<<< HEAD
=======
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

>>>>>>> d2ce44e041cf239debaeb29d9e16758f23fe42b8
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



<<<<<<< HEAD
#get_answer("What does CPR stand for ?")
=======
q = "Who directed Titanic ? "
answer = get_answer(q)
#print "\nAnswer : \t-> | ",answer
>>>>>>> d2ce44e041cf239debaeb29d9e16758f23fe42b8
