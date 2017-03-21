from practnlptools.tools import Annotator
import wikipedia
from sparqlquery import *
from difflib import SequenceMatcher
from SPARQLWrapper import SPARQLWrapper, JSON
import webbrowser
from question_processing.target_extraction import remove_fine_target
import unicodedata

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
annotator = Annotator()

wikipedia.set_lang('en')

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_capitals(list):
    capital=[]
    all_element=[]
    for element in list:
        element=element.split()
        for e in element:
            all_element.append(e)
    for i in range(0,len(all_element)):
        if all_element[i][0].isupper():
            capital.append(all_element[i])
    return capital

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
                    #print answer
            else:
                if result["x"]["xml:lang"] == "en":
                    ret_answer = unicodedata.normalize('NFKD', result["x"]["value"]).encode('ascii','ignore')
        print "CHECK : ",ret_answer
        print "CHECK TYPE : ",type(ret_answer)
        return ret_answer
    else:
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


def get_query(fine_class,target,special_words):
    query=None
    if fine_class == "mountain":
        to_search = ""
        for t in target:
            to_search = to_search+" "+t

        search_result = wikipedia.search(to_search)
        page = search_result[0]
        if page.split("_")[0] in ["List","list"]:
            print "Answer not found in DBpedia(English)"
            webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
            print "\n"
            return
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

    elif fine_class == "other":
        target=remove_fine_target(target,fine_class)
        to_search = ""
        for t in target:
            to_search = to_search+" "+t
        search_result = wikipedia.search(to_search)
        page = search_result[0]
        if page.split("_")[0] in ["List","list"]:
            print "Answer not found in DBpedia(English)"
            webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
            print "\n"
            return
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

    elif fine_class == "country":
        target=remove_fine_target(target,fine_class)
        to_search = ""
        for t in target:
            to_search = to_search+" "+t

        search_result = wikipedia.search(to_search)
        page = search_result[0]
        if page.split("_")[0] in ["List","list"]:
            print "Answer not found in DBpedia(English)"
            webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
            print "\n"
            return
        print page
        wiki_page = wikipedia.page(page)
        wiki_url = wiki_page.url
        resource_page = ""
        resource_page = wiki_url.split('/')[4]

        dbpedia_base ="http://dbpedia.org/resource/"
        uri =  Namespace(dbpedia_base+resource_page)
        query= Select([v.x]).where((uri, RDFS.comment,v.x))
        query = query.compile()
        print "\nQUERY : ",query


    elif fine_class == "state":
        #target=remove_fine_target(target,fine_class)
        to_search=""
        if special_words==[]:
            capital=get_capitals(target)
            if  capital!=[]:
                for element in capital:
                    to_search=to_search+element
            else:
                for t in target:
                    to_search = to_search+" "+t
        else:
            for element in special_words:
                target.append(element)
            for t in target:
                to_search = to_search+" "+t
        search_result = wikipedia.search(to_search)
        page = search_result[0]
        if page.split("_")[0] in ["List","list"]:
            print "Answer not found in DBpedia(English)"
            webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
            print "\n"
            return
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

    if query!=None:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        print "\nAnswer : "
        check=display_answer(results)
        if check==False:
            print "Answer not found in DBpedia(English)"
            webbrowser.open("https://en.wikipedia.org/wiki/"+page)
            print "\n"
            return
        """
        elif check==False:
            to_search = ""
            for t in target:
                for element in t.split():
                    if element.isupper():
                        to_search = element

            DBO = Namespace("http://dbpedia.org/ontology/")
            dbpedia_base ="http://dbpedia.org/resource/"
            uri =  Namespace(dbpedia_base+to_search)
            property_list=get_properties(to_search)

            for properties in property_list:
                if properties=="wikiPageDisambiguates":
                    query=Select([v.x]).where((uri,DBO.wikiPageDisambiguates,v.x))
                    query=query.compile()
            if query!=None:
                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                results = sparql.query().convert()
                check=display_answer(results)
                if check==False:
                    to_search = ""
                    for t in target:
                        if t.isupper():
                            to_search = to_search+" "+t
                    search_result = wikipedia.search(to_search)
                    page = search_result[0]
                    wiki_page=None
                    try:
                        wiki_page = wikipedia.page(page)
                    except wikipedia.exceptions.DisambiguationError as e:
                        print e.options
                        wiki_page= wikipedia.page(wikipedia.search(e.options[0])[0])
                    wiki_url = wiki_page.url
                    resource_page = ""
                    resource_page = wiki_url.split('/')[4]
                    DBO = Namespace("http://dbpedia.org/ontology/")
                    dbpedia_base ="http://dbpedia.org/resource/"
                    uri =  Namespace(dbpedia_base+resource_page)
                    query= Select([v.x]).where((uri, DBO.abstract,v.x))
                    query = query.compile()
                    if query!=None:
                        sparql.setQuery(query)
                        sparql.setReturnFormat(JSON)
                        results = sparql.query().convert()
                        check=display_answer(results)
                        if check==False:
                            print "Answer not found in DBpedia(English)"
                            webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
                            print "\n"
            """
