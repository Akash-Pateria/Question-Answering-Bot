from practnlptools.tools import Annotator
import wikipedia
from sparqlquery import *

annotator = Annotator()

wikipedia.set_lang('en')

def get_query(fine_class,target,special_words):
    if fine_class == 'description':
        to_search = ""
        for t in target:
            to_search = to_search+" "+t
            search_result = wikipedia.search(to_search)
        page = search_result[0]
        wiki_page = wikipedia.page(page)
        wiki_url = wiki_page.url
        resource_page = ""
        print "\nRESOURCE : ",resource_page
        resource_page = wiki_url.split('/')[-1]
        dbpedia_base ="http://dbpedia.org/resource/"
        uri =  Namespace(dbpedia_base+resource_page)
        query = Select([v.x]).where((uri, RDFS.comment,v.x))
        return 'x',query.compile()

    elif fine_class == 'individual':
        to_search = ""
        for t in target:
            to_search = to_search+" "+t
            search_result = wikipedia.search(to_search)
        page = search_result[0]
        wiki_page = wikipedia.page(page)
        wiki_url = wiki_page.url
        resource_page = ""
        resource_page = wiki_url.split('/')[-1]
        dbpedia_base ="http://dbpedia.org/resource/"
        print "\nRESOURCE : ",resource_page
        uri =  Namespace(dbpedia_base+resource_page)
        query = Select([v.x]).where((uri, RDFS.comment,v.x))
        return 'x',query.compile()

    else:
        return 'None',None
