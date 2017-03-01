from practnlptools.tools import Annotator
import nltk
import re

def preprocess(raw_sentence):
    sentence= re.sub(r'[$|!|.|(|)|,|;]',r'',raw_sentence)
    sentence = re.sub(r'[\-|/]',r' ',sentence)
    return sentence

def quote_preprocess(raw_sentence):
    sentence= re.sub(r'[$|!|"|`|\'|(|)|,|;]',r'',raw_sentence)
    sentence = re.sub(r'[\-|/]',r' ',sentence)
    return sentence


def equal_quote(line):
    line_r=line.split()
    c1=c2=c3=0
    for i in range(0,len(line_r)):
        if line_r[i]=='\'':
            c1=c1+1
        if line_r[i]=='"':
            c2=c2+1
        if line_r[i]=='`':
            c3=c3+1
    if c1%2==0 and c2%2==0 and c3%2==0:
        return True
    else:
        return False


def extract_special_meaning(question):
    question = question.split()
    new_question = ""
    special_meaning_words = []
    temp_word = ""
    i=0
    while i < len(question):
        if question[i] in ['\'','"','`','``','\'\'']:
            i=i+1
            while question[i] not in ['\'','"','`','``','\'\'']:
                if temp_word == "":
                    temp_word = temp_word+question[i]
                else:
                    temp_word = temp_word +" "+ question[i]
                i=i+1
            special_meaning_words.append(temp_word)
        else:
            if new_question == "":
                new_question = new_question+question[i]
            else:
                new_question = new_question+" "+question[i]
        i=i+1
    return special_meaning_words, new_question


def compute_capitals(line):
    line_r = line.split()
    noun=[]
    index=[]
    for i in range(1,len(line_r)):
        if line_r[i][0].isupper():
            noun.append(line_r[i])
            index.append(i)
    return noun,index


def refine_capitals(line,target_index):
    noun,noun_index=compute_capitals(line)
    not_included_index=[]
    for index in noun_index:
        if index not in target_index:
            not_included_index.append(index)
            for i in range(0,len(target_index)):
                if target_index[i]>index:
                    target_index.insert(i,index)
                    break

    target=[]
    line=line.split()
    for i in range(0,len(target_index)):
        if target_index[i] in not_included_index:
            if target==[]:
                target.append(line[target_index[i]])
            else:
                temp_str=""
                temp_str=target[-1]+" "+line[target_index[i]]
                del target[-1]
                target.append(temp_str)
        else:
            target.append(line[target_index[i]])
    return target


def compute_POS(line):
    annotator=Annotator()
    pos=annotator.getAnnotations(line)['pos']
    pos_tag=[]
    for p in pos:
        pos_tag.append(p[1])
    return pos_tag


def compute_NER(line):
    annotator=Annotator()
    ner=annotator.getAnnotations(line)['ner']
    ner_tag=[]
    for n in ner:
        ner_tag.append(n[1])
    return ner_tag

def get_index(list_r,element):
    for i in range(0,len(list_r)):
        if list_r[i]==element:
            return i
    return -1


def extract_target(question):
    POS=compute_POS(question)
    NER=compute_NER(question)
    flag=0;
    index = []
    target=[]
    """
    for ner in NER:
        if ner not in ['O']:
            flag=1
            break

    if flag==0:
        for i in range(0,len(POS)):
            if POS[i] in ['NN','NNP','NNS','NNPS','RB','RBS','RBR','CD','FW','JJ','JJS','JJR']:
                index.append(i)

    else:
        for i in range(0,len(NER)):
            if NER[i] not in ['O']:
                index.append(i)
    """

    for i in range(0,len(POS)):
        if POS[i] in ['NN','NNP','NNS','NNPS','RB','RBS','RBR','CD','FW','JJ','JJS','JJR']:
            index.append(i)

    question = question.split()
    for i in index:
        target.append(question[i])
    return target,index


def merge_similar_target(line,target_index):
    line = line.split()
    temp_target=[]
    if len(target_index) > 1 :
        current_index=target_index[0]
        flag=0
        for i in range(0,len(target_index)-1):
            if current_index + 1==target_index[i+1]:
                temp_str=""
                if temp_target==[]:
                    temp_str=line[current_index] + " " + line[target_index[i+1]]
                    current_index=target_index[i+1]
                    temp_target.append(temp_str)
                else:
                    if flag==1:
                        temp_str=temp_target[-1]+" "+line[target_index[i+1]]
                        current_index=target_index[i+1]
                        del temp_target[-1]
                        temp_target.append(temp_str)
                    else:
                        temp_str=line[current_index]+" "+line[target_index[i+1]]
                        current_index=target_index[i+1]
                        temp_target.append(temp_str)
                flag=1
            else:
                if flag != 1 or temp_target==[]:
                    temp_target.append(line[current_index])
                    current_index=target_index[i+1]
                else:
                    current_index=target_index[i+1]
                flag=0
    else:
        for i in target_index:
            temp_target.append(line[i])
    return temp_target



###########################################################################################################################

file_r = open("questions.txt","r")
file_w = open("target.txt","w")

for line in file_r:
    if not (equal_quote(line)):
        line =quote_preprocess(line)

    special_word,line = extract_special_meaning(line)
    line  = preprocess(line)

    target,target_index=extract_target(line)

    target=refine_capitals(line,target_index)

    target=merge_similar_target(line,target_index)
    if special_word==[]:
        print line," :: ",target
        file_w.write(' '.join(str(e) for e in target)+"\n")

    else:
        print line," :: ",extract_target(line)," Special Words :: ", special_word
        file_w.write(' '.join(str(e) for e in target)+"\t\t\tSpecial Words ::"+' '.join(str(e) for e in special_word)+"\n")

file_w.close()
file_r.close()
