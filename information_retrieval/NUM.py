from practnlptools.tools import Annotator
import wikipedia
from SPARQLWrapper import SPARQLWrapper, JSON
from sparqlquery import *

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
annotator = Annotator()

dbo = Namespace("http://dbpedia.org/ontology/")

wikipedia.set_lang('en')

def get_query(fine_class,target,special_words):
    if fine_class == 'date':
        #finding the resource page
        to_search = ""
        for t in target:
            to_search = to_search+" "+t
            search_result = wikipedia.search(to_search)
        page = search_result[0]
        wiki_page = wikipedia.page(page)
        wiki_url = wiki_page.url
        resource_page = ""
        resource_page = wiki_url.split('/')[-1]
        print "\nRESOURCE : ",resource_page

        #forming the query
        dbpedia_base ="http://dbpedia.org/resource/"
        uri =  Namespace(dbpedia_base+resource_page)
        query = Select([v.x]).where((uri, dbo.birthDate,v.x))
        query = query.compile()
        print "\nQUERY : \n",query

        # retrieving data from the dbpedia page
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        #printing the resuts
        print "\nAnswer : \n"
        for result in results["results"]["bindings"]:
            print result["x"]["value"]

    elif fine_class == 'distance':
        #finding the resource page
        to_search = ""
        for t in target:
            to_search = to_search+" "+t
            search_result = wikipedia.search(to_search)
        page = search_result[0]
        wiki_page = wikipedia.page(page)
        wiki_url = wiki_page.url
        resource_page = ""
        resource_page = wiki_url.split('/')[-1]
        print "\nRESOURCE : ",resource_page

        #forming the query
        dbpedia_base ="http://dbpedia.org/resource/"
        uri =  Namespace(dbpedia_base+resource_page)
        query = Select([v.x]).where((uri, RDFS.comment,v.x))
        query = query.compile()
        print "\nQUERY : \n",query

        # retrieving data from the dbpedia page
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        #printing the resuts
        print "\nAnswer : \n"
        for result in results["results"]["bindings"]:
            if result["x"]["xml:lang"] == "en":
                print result["x"]["value"]

    else:
        return 'None',None
