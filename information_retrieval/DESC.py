from practnlptools.tools import Annotator
import wikipedia
from sparqlquery import *
from difflib import SequenceMatcher
from SPARQLWrapper import SPARQLWrapper, JSON
import webbrowser
import unicodedata

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
annotator = Annotator()

wikipedia.set_lang('en')

def display_answer(results):
    ret_answer = ""
    if results["results"]["bindings"]!=[]:
        for result in results["results"]["bindings"]:
            if result["x"]["value"].split(":")[0]=="http":
                if len(result["x"]["value"].split("/")[-1].split("_"))>1:
                    answer=""
                    for element in result["x"]["value"].split("/")[-1].split("_"):
                        answer=answer+" "+element
                        ret_answer = answer
                    #print answer#
                else:
                    #print result["x"]["value"].split("/")[-1]#
                    ret_answer = unicodedata.normalize('NFKD', result["x"]["value"].split("/")[-1]).encode('ascii','ignore')

            else:
                if result["x"]["xml:lang"] == "en":
                    #print result["x"]["value"]#
                    ret_answer = unicodedata.normalize('NFKD', result["x"]["value"]).encode('ascii','ignore')
        #print "CHECK : ",ret_answer
        #print "CHECK TYPE : ",type(ret_answer)
        return ret_answer
    else:
        #print "\nAnswer not found in DBpedia\n"
        return ret_answer

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

def try_except(page):
    try:
        page = wikipedia.page(page)
        wiki_url = page.url
    except wikipedia.exceptions.DisambiguationError:
        wiki_url = wikipedia.search(page)
        wiki_url=wiki_url[1:]
        choice=0
        #print "\nInput question may refer to:\n "
        #for i, topic in enumerate(topics):
            #print i, topic
        #choice = int(raw_input("\nEnter a choice: "))
        #assert choice in xrange(len(topics))
        wiki_url=wikipedia.page(wikipedia.search(wiki_url[choice])[0]).url
    return wiki_url

def get_query(fine_class,target,special_words):
    ret_answer = ""
    if special_words!=[]:
        for element in special_words:
            target.append(element)
    if fine_class in ["definition","description"]:
        to_search = ""
        for t in target:
            to_search = to_search+" "+t

        search_result = wikipedia.search(to_search)
        page = search_result[0]
        if page.split("_")[0] in ["List","list","Lists"]:
            #print "Answer found in DBpedia(English) as list of information"
            #webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
            return ""
        #################################################################
        wiki_url=try_except(page)
        ################################################################
        resource_page = ""
        resource_page = wiki_url.split('/')[4]
        DBO = Namespace("http://dbpedia.org/ontology/")
        dbpedia_base ="http://dbpedia.org/resource/"
        uri =  Namespace(dbpedia_base+resource_page)
        query= Select([v.x]).where((uri, RDFS.comment,v.x))
        query = query.compile()
        print "\nQUERY : ",query

    elif fine_class == "manner":
        return ""

    elif fine_class == "reason":
        return ""

    else:
        query=None


    if query!=None:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        return display_answer(results)
    else:
        print"\nQuery could not formed\n"
