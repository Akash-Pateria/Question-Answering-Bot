from practnlptools.tools import Annotator
import wikipedia
from sparqlquery import *
from difflib import SequenceMatcher
from SPARQLWrapper import SPARQLWrapper, JSON
import webbrowser

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
annotator = Annotator()

wikipedia.set_lang('en')

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def get_properties(uri,page):
    temp_query="select distinct ?property{\
    { <http://dbpedia.org/resource/" + page + "> ?property ?o }\
    union\
    { ?s ?property <http://dbpedia.org/resource/" + page + "> }\
    optional {\
    ?property rdfs:label ?label\
    }}"
    property_list=[]
    sparql.setQuery(temp_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        property_list.append(result["property"]["value"])
    return property_list


def get_query(fine_class,target,special_words):
    if fine_class in ["definition","description"]:
        to_search = ""
        for t in target:
            to_search = to_search+" "+t

        search_result = wikipedia.search(to_search)
        page = search_result[0]
        wiki_page = wikipedia.page(page)
        wiki_url = wiki_page.url
        resource_page = ""
        resource_page = wiki_url.split('/')[4]
        DBO = Namespace("http://dbpedia.org/ontology/")
        dbpedia_base ="http://dbpedia.org/resource/"
        uri =  Namespace(dbpedia_base+resource_page)
        query= Select([v.x]).where((uri, DBO.abstract,v.x))
        query = query.compile()
        print "\nQUERY : ",query

    else:
        query=None
        
    """
    elif fine_class == "manner":
        ##
        verb=[]
        to_search = ""
        for t in target:
            if len(t.split())>1:
                for element in t.split():
                    if annotator.getAnnotations(element)['pos'][1] in ['NN','NNP','NNS','NNPS']:
                        to_search = to_search+" "+element
            else:
                if annotator.getAnnotations(t)['pos'][1] in ['NN','NNP','NNS','NNPS']:
                    to_search = to_search+" "+t
                if annotator.getAnnotations(t)['pos'][1] in ['VB','VBS']:
                    verb.append(t)
        ##
        to_search = ""
        for t in target:
            to_search = to_search+" "+t
        search_result = wikipedia.search(to_search)
        page = search_result[0]
        wiki_page = wikipedia.page(page)
        wiki_url = wiki_page.url
        resource_page = ""
        resource_page = wiki_url.split('/')[4]

        dbpedia_base ="http://dbpedia.org/resource/"
        uri =  Namespace(dbpedia_base+resource_page)
        query= Select([v.x]).where((uri, RDFS.comment,v.x))
        query = query.compile()
        print "\nQUERY : ",query

    elif fine_class == "reason":
        to_search = ""
        for t in target:
            to_search = to_search+" "+t

        search_result = wikipedia.search(to_search)
        page = search_result[0]
        wiki_page = wikipedia.page(page)
        wiki_url = wiki_page.url
        resource_page = ""
        resource_page = wiki_url.split('/')[4]

        dbpedia_base ="http://dbpedia.org/resource/"
        uri =  Namespace(dbpedia_base+resource_page)
        query= Select([v.x]).where((uri, RDFS.comment,v.x))
        query = query.compile()
        print "\nQUERY : ",query
    """



    if query!=None:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        print "\nAnswer : \n"
        if results["results"]["bindings"]!=[]:
            for result in results["results"]["bindings"]:
                if result["x"]["xml:lang"] == "en":
                    print result["x"]["value"]
        else:
            print "Answer not found in DBpedia(English)"
            webbrowser.open("https://en.wikipedia.org/wiki/"+resource_page)
        print "\n"
    else:
        print"\nQuery could not formed\n"
