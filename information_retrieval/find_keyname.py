from dbpedia_property import get_property_name
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import wordnet as wn
from practnlptools.tools import Annotator
from nltk.corpus import stopwords

stemmer = SnowballStemmer("english")
stop_words = set(stopwords.words('english'))
annotator = Annotator()


def word_syn(word):
    req_words = []

    syns = wn.synsets(word)[:3]

    for s in syns:
        for name in s.lemma_names():
            if name not in req_words:
                pos_t = annotator.getAnnotations(name)['pos']
                if pos_t[0][1] in ['NN','NNS','NNP','NNPS'] and name not in stop_words:
                    req_words.append(stemmer.stem(name))

    return req_words

def get_req_keyname(uri,target_findkey,fine_class):
    req_keyname = ""
    temp_keyname = ["",0]
    property_key = []
    property_list = get_property_name(uri)
    fine_class_list = word_syn(fine_class)
    for p in property_list:
        key = p.split('/')
        key = key[-1].lower()
        property_key.append(key)

    temp = []
    x_temp = target_findkey
    #print "\nTARGET FIND : ",target_findkey
    for t in target_findkey:
        syn_list = word_syn(t)
        for s in syn_list:
            if s not in temp:
                temp.append(stemmer.stem(s))
    target_findkey = temp

    for x in x_temp:
        target_findkey.append(stemmer.stem(x))

    temp = []
    for p in target_findkey:
        p=p.split('_')
        for x in p:
            temp.append(x)
    target_findkey = temp
    temp = []
    for p in target_findkey:
        p=p.split('(')
        for x in p:
            temp.append(x)
    target_findkey = temp
    temp = []
    for p in target_findkey:
        p=p.split(')')
        for x in p:
            if len(x)>2:
                temp.append(x)
    target_findkey = temp

    #print "\nAFTER SYN : ",target_findkey
    #print "\n FINE CLASS SYN : ",fine_class_list

    for i in range(0,len(property_key)):
        key_score = 0
        check = False
        for t in target_findkey:
            if t in property_key[i] or property_list[i] in t:
                key_score = key_score + 2
                break

        for f in fine_class_list:
            if f in property_key[i] or property_key[i] in f:
                key_score = key_score + 1
                check = True
                break

        #print "\nKEY : ",property_list[i],"\t SCORE : ",key_score

        if fine_class == "date" and check:
            if key_score > 0 and temp_keyname[1] < key_score:
                temp_keyname[0]=property_list[i]
                temp_keyname[1]=key_score
        elif fine_class != "date":
            if key_score > 0 and temp_keyname[1] < key_score:
                temp_keyname[0]=property_list[i]
                temp_keyname[1]=key_score

    req_keyname = temp_keyname[0]
    #print "\nRETURN KEY : ",req_keyname
    return req_keyname
