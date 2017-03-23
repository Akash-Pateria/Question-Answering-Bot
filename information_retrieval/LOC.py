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

def fixed_answer_extraction(to_search,type):
    search_result = wikipedia.search(to_search)
    page = search_result[0]
    if page.split()[0] in ["List","list","Lists"]:
        #print "Answer found in DBpedia(English) as list of information"
        #webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
        return ""
    wiki_url=try_except(page)
    resource_page = ""
    resource_page = wiki_url.split('/')[-1]
    DBO = Namespace("http://dbpedia.org/ontology/")
    dbpedia_base ="http://dbpedia.org/resource/"
    uri =  Namespace(dbpedia_base+resource_page)
    if type=="comment":
        query= Select([v.x]).where((uri, RDFS.comment,v.x))
    elif type=="abstract":
        query= Select([v.x]).where((uri, DBO.abstract,v.x))

    query = query.compile()
    return query

def get_ans(query):
    if query!=None:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        return display_answer(results)

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
    if fine_class == "mountain":
        to_search = ""
        if special_words!=[]:
            for element in special_words:
                target.append(element)
        for t in target:
            to_search = to_search+" "+t
        """
        query=fixed_answer_extraction(to_search,"abstract")
        if query!="":
            print "\nQUERY : ",query
            return get_ans(query)
        else:
            return ""

        """
        search_result = wikipedia.search(to_search)
        page = search_result[0]
        if page.split("_")[0] in ["List","list","Lists"]:
            #print "Answer found as list of information"
            #webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
            return ""
        wiki_url=try_except(page)
        resource_page = ""
        resource_page = wiki_url.split('/')[-1]
        DBO = Namespace("http://dbpedia.org/ontology/")
        dbpedia_base ="http://dbpedia.org/resource/"
        uri =  Namespace(dbpedia_base+resource_page)
        query= Select([v.x]).where((uri, DBO.abstract,v.x))
        query = query.compile()


    elif fine_class == "other":
        target=remove_fine_target(target,fine_class)
        if special_words!=[]:
            for element in special_words:
                target.append(element)
        to_search = ""
        for t in target:
            to_search = to_search+" "+t
        """
        query=fixed_answer_extraction(target,"abstract")
        if query!="":
            print "\nQUERY : ",query
            return get_ans(query)
        else:
            return ""
        """
        search_result = wikipedia.search(to_search)
        page = search_result[0]
        if page.split("_")[0] in ["List","list","Lists"]:
            #print "Answer found in DBpedia(English) as list of information"
            #webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
            return ""
        wiki_url=try_except(page)
        resource_page = ""
        resource_page = wiki_url.split('/')[-1]
        DBO = Namespace("http://dbpedia.org/ontology/")
        dbpedia_base ="http://dbpedia.org/resource/"
        uri =  Namespace(dbpedia_base+resource_page)
        query= Select([v.x]).where((uri, DBO.abstract,v.x))
        query = query.compile()


    elif fine_class == "city":
        #target=remove_fine_target(target,fine_class)
        to_search = ""
        if (special_words!=[]) and ("capital" in target):
            #target.remove("capital")
            for t in special_words:
                to_search = to_search+" "+t
            search_result = wikipedia.search(to_search)
            page = search_result[0]
            if page.split("_")[0] in ["List","list","Lists"]:
                #print "Answer found in DBpedia(English) as list of information"
                #webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
                return ""
            wiki_url=try_except(page)
            resource_page = ""
            resource_page = wiki_url.split('/')[-1]
            property_list=get_properties(resource_page)
            DBO = Namespace("http://dbpedia.org/ontology/")
            dbpedia_base ="http://dbpedia.org/resource/"
            uri =  Namespace(dbpedia_base+page)
            for properties in property_list:
                if properties=="capital":
                    query=Select([v.x]).where((uri,DBO.capital,v.x))
                    query=query.compile()
                    print "\nQUERY : ",query
                    return get_ans(query)
        else:
            if special_words!=[]:
                for t in special_words:
                    target.append(t)
                for t in target:
                    to_search = to_search+" "+t


                query=fixed_answer_extraction(to_search,"comment")
                if query!="":
                    print "\nQUERY : ",query
                    return get_ans(query)
                else:
                    return ""


            if "capital" in target:
                target.remove("capital")
                for t in target:
                    to_search = to_search+" "+t
                search_result = wikipedia.search(to_search)
                page = search_result[0]
                if page.split("_")[0] in ["List","list","Lists"]:
                    #print "Answer found in DBpedia(English) as list of information"
                    #webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
                    return ""
                wiki_url=try_except(page)
                resource_page = ""
                resource_page = wiki_url.split('/')[-1]
                property_list=get_properties(resource_page)
                DBO = Namespace("http://dbpedia.org/ontology/")
                dbpedia_base ="http://dbpedia.org/resource/"
                uri =  Namespace(dbpedia_base+resource_page)
                for properties in property_list:
                    if properties=="capital":
                        query=Select([v.x]).where((uri,DBO.capital,v.x))
                        query=query.compile()
                        print "\nQUERY : ",query
                        return get_ans(query)

        if (special_words==[]) and ("capital" not in target):
            for t in target:
                to_search = to_search+" "+t
            query=fixed_answer_extraction(to_search,"comment")
            if query!="":
                print "\nQUERY : ",query
                return get_ans(query)
            else:
                return ""

    elif fine_class == "country":
        target=remove_fine_target(target,fine_class)
        to_search = ""
        if special_words!=[]:
            for element in special_words:
                target.append(element)
        for t in target:
            to_search = to_search+" "+t
        """
        query=fixed_answer_extraction(to_search,"comment")
        if query!="":
            print "\nQUERY : ",query
            return get_ans(query)
        else:
            return ""
        """
        search_result = wikipedia.search(to_search)
        page = search_result[0]
        if page.split("_")[0] in ["List","list","Lists"]:
            #print "Answer found in DBpedia(English) as list of information"
            #webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
            return ""
        wiki_url=try_except(page)
        resource_page = ""
        resource_page = wiki_url.split('/')[-1]

        dbpedia_base ="http://dbpedia.org/resource/"
        uri =  Namespace(dbpedia_base+resource_page)
        query= Select([v.x]).where((uri, RDFS.comment,v.x))
        query = query.compile()



    elif fine_class == "state":
        target=remove_fine_target(target,fine_class)
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
        if page.split("_")[0] in ["List","list","Lists"]:
            #print "Answer found in DBpedia(English) as list of information"
            #webbrowser.open("https://en.wikipedia.org/wiki/"+to_search)
            return ""
        wiki_url=try_except(page)
        resource_page = ""
        resource_page = wiki_url.split('/')[4]
        DBO = Namespace("http://dbpedia.org/ontology/")
        dbpedia_base ="http://dbpedia.org/resource/"
        uri =  Namespace(dbpedia_base+resource_page)
        query= Select([v.x]).where((uri, DBO.abstract,v.x))
        query = query.compile()

        """
        query=fixed_answer_extraction(to_search,"comment")
        if query!="":
            print "\nQUERY : ",query
            return get_ans(query)
        else:
            return ""
        """


    else:
        query=None

    print "\nQUERY : ",query

    if query!=None:
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()

        return display_answer(results)
