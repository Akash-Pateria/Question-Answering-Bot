from nltk.corpus import wordnet as wn
from nltk.stem.snowball import SnowballStemmer
from practnlptools.tools import Annotator
import en

annotator = Annotator()
stemmer = SnowballStemmer("english")

def nounify_verb(word):
    set_of_related_nouns = set()
    req_words = []

    for lemma in wn.lemmas(wn.morphy(word,wn.VERB), pos="v"):
        for related_form in lemma.derivationally_related_forms():
            for synset in wn.synsets(related_form.name(), pos=wn.NOUN):
                if wn.synset('person.n.01') in synset.closure(lambda s:s.hypernyms()):
                    set_of_related_nouns.add(synset)

    for w in set_of_related_nouns:
        for name in w.lemma_names():
            if name not in req_words:
                req_words.append(name)

    return req_words

def word_syn(word):
    req_words = []

    syns = wn.synsets(word)[:3]

    for s in syns:
        for name in s.lemma_names():
            if name not in req_words:
                req_words.append(stemmer.stem(name))

    return req_words

def get_near_page(search,target,coarse_class):
    page_index = [0,0]
    temp_target = []
    for t in target:
        words = t.split()
        for w in words:
            temp_target.append(w)
    target = temp_target

    for i in range(0,len(search)):
        score = 0
        p_name =search[i].split()
        temp = []
        for p in p_name:
            temp.append(p)
        p_name = temp
        temp = []
        for p in p_name:
            p=p.split('_')
            for x in p:
                temp.append(x)
        p_name = temp
        temp = []
        for p in p_name:
            p=p.split('(')
            for x in p:
                temp.append(x)
        p_name = temp
        temp = []
        for p in p_name:
            p=p.split(')')
            for x in p:
                temp.append(x)
        p_name = temp
        for t in target:
            pos_t = annotator.getAnnotations(t)['pos']
            if coarse_class == "HUM" and pos_t[0][1] in ['VBD','VBG','VBN','VBP','VBZ']:
                req_word = en.verb.infinitive(t)
                if req_word == "":
                    req_word = t
                syn_list = nounify_verb(req_word)
            else:
                syn_list = word_syn(t)
            temp = []
            for p in syn_list:
                p=p.split('_')
                for x in p:
                    temp.append(x)
            syn_list = temp
            temp = []
            for p in syn_list:
                p=p.split('(')
                for x in p:
                    temp.append(x)
            syn_list = temp
            temp = []
            for p in syn_list:
                p=p.split(')')
                for x in p:
                    temp.append(x)
            syn_list = temp

            for w in p_name:
                for s in syn_list:
                    if s in w or w in s:
                        score = score + 1

        if page_index[1] < score:
            page_index[0]=i
            page_index[1]=score

    return page_index[0]
