from practnlptools.tools import Annotator
import wikipedia
from sparqlquery import *
from SPARQLWrapper import SPARQLWrapper, JSON
import webbrowser
from question_processing.target_extraction import remove_fine_target
import unicodedata

sparql = SPARQLWrapper("http://dbpedia.org/sparql")
annotator = Annotator()
wikipedia.set_lang('en')

def get_index(list,key):
    for i in range(0,len(list)):
        if list[i]==key:
            return i

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
                    print result["x"]["value"].split("/")[-1]
            else:
                if result["x"]["xml:lang"] == "en":
                    ret_answer = unicodedata.normalize('NFKD', result["x"]["value"]).encode('ascii','ignore')
        return ret_answer
    else:
        return ret_answer


def get_properties(page):
    temp_query="select distinct ?property{\
    { <http://dbpedia.org/resource/" + page + "> ?property ?o }\
    union\
    { ?s ?property <http://dbpedia.org/resource/" + page + "> }\
    }"
    property_list=[]
    sparql.setQuery(temp_query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    for result in results["results"]["bindings"]:
        property_list.append(str(result["property"]["value"]).split("/")[-1])
    return property_list


def get_query(fine_class,target,special_words):
    query=None
    if fine_class == "expression":
        to_search = ""
        if special_words!=[]:
            for element in special_words:
                target.append(element)
        for t in target:
            for element in t.split():
                if element.isupper():
                    to_search = element
        search_result = wikipedia.search(to_search)
        page = search_result[0]
        if page.split("_")[0] in ["List","list","Lists"]:
            #print "Answer found in DBpedia(English) as list of information"
            #webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
            return ""
        wiki_page = wikipedia.page(page)
        wiki_url = wiki_page.url
        resource_page = ""
        resource_page = wiki_url.split('/')[-1]
        DBO = Namespace("http://dbpedia.org/ontology/")
        dbpedia_base ="http://dbpedia.org/resource/"
        uri =  Namespace(dbpedia_base+resource_page)
        query= Select([v.x]).where((uri, RDFS.comment,v.x))
        query = query.compile()

        print "\nQUERY : \n",query

    if fine_class=="abbreviation":
        target=remove_fine_target(target,fine_class)
        simple = []
        complx=[]
        if special_words!=[]:
            for element in special_words:
                target.append(element)
        for t in target:
            for element in t.split():
                if element not in ["abbreviation","Abbreviation","abbreviated","expression"]:
                    if element[0].isupper():
                        simple.append(element)
                    else:
                        complx.append(element)
        if len(simple)>1:
            answer=""
            for element in simple:
                answer=answer+element[0]
            return answer
        else:
            if simple==[]:
                to_search=""
                for element in complx:
                    if to_search=="":
                        to_search=element
                    else:
                        to_search=to_search+" "+element
                search_result = wikipedia.search(to_search)
                page = search_result[0]
                if page.split("_")[0] in ["List","list","Lists"]:
                    #print "Answer found in DBpedia(English) as list of information"
                    #webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
                    return ""
                wiki_page = wikipedia.page(page)
                wiki_url = wiki_page.url
                resource_page = ""
                resource_page = wiki_url.split('/')[-1]
                property_list=get_properties(resource_page)
                DBO = Namespace("http://dbpedia.org/ontology/")
                dbpedia_base ="http://dbpedia.org/resource/"
                uri =  Namespace(dbpedia_base+resource_page)
                for properties in property_list:
                    if properties=="wikiPageDisambiguates":
                        query=Select([v.x]).where((uri,DBO.wikiPageDisambiguates,v.x))
                        query=query.compile()
            else:
                DBO = Namespace("http://dbpedia.org/ontology/")
                dbpedia_base ="http://dbpedia.org/resource/"
                uri =  Namespace(dbpedia_base+simple[0])
                property_list=get_properties(simple[0])
                for properties in property_list:
                    if properties=="wikiPageDisambiguates":
                        query=Select([v.x]).where((uri,DBO.wikiPageDisambiguates,v.x))
                        query=query.compile()
                #webbrowser.open("https://en.wikipedia.org/wiki/"+simple[0])
        print "\nQUERY : \n",query

    if query!=None:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        check=display_answer(results)
        if check=="" and fine_class!="abbreviation":
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
                if check=="":
                    to_search = ""
                    for t in target:
                        if t.isupper():
                            to_search = to_search+" "+t
                    search_result = wikipedia.search(to_search)
                    page = search_result[0]
                    if page.split("_")[0] in ["List","list","Lists"]:
                        #print "Answer found in DBpedia(English) as list of information"
                        #webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
                        return ""
                    wiki_page=None
                    #try:
                    wiki_page = wikipedia.page(page)
                    #except wikipedia.exceptions.DisambiguationError as e:
                    #    print e.options
                    #wiki_page= wikipedia.page(wikipedia.search(e.options[0])[0])
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
                        if check=="":
                            return ""
                            #webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
                            #print "\n"
        else:
            return check
