from dbpedia_property import get_property_name
from nltk.corpus import wordnet as wn

def fine_class_syn(word):
    req_words = []

    syns = wn.synsets(word)

    for s in syns:
        for name in s.lemma_names():
            if name not in req_words:
                req_words.append(name)

    return req_words

def get_req_keyname(uri,target_findkey,fine_class):
    req_keyname = ""
    temp_keyname = ["",0]
    property_key = []
    property_list = get_property_name(uri)
    fine_class_list = fine_class_syn(fine_class)
    for p in property_list:
        key = p.split('/')
        key = key[-1].lower()
        property_key.append(key)

    for i in range(0,len(property_key)):
        key_score = 0
        for t in target_findkey:
            if t in property_key[i] or property_list[i] in t:
                key_score = key_score + 1

        for f in fine_class_list:
            if f in property_key[i] or property_key[i] in f:
                key_score = key_score + 1
                break

        if fine_class == "date":
            if key_score > 1 and temp_keyname[1] < key_score:
                temp_keyname[0]=property_list[i]
                temp_keyname[1]=key_score
        else:
            if key_score > 0 and temp_keyname[1] < key_score:
                temp_keyname[0]=property_list[i]
                temp_keyname[1]=key_score

    req_keyname = temp_keyname[0]

    if temp_keyname == "":
        return "None"
    else:
        return req_keyname
