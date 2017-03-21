from practnlptools.tools import Annotator
from nltk.corpus import stopwords
from question_classification import get_classes
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


def same_case(word1,word2):
    if word1[0].isupper() and word2[0].isupper():
        return True
    elif word1[0].islower() and word2[0].islower():
        return True
    elif word1.isdigit() and word2[0].islower():
        return  True
    elif word1.isdigit() and word2[0].isupper():
        return  True
    elif word1[0].isupper() and word2.isdigit():
        return  True
    elif word1[0].islower() and word2.isdigit():
        return  True
    else:
        return False


def refine_capitals(line,target_index):
    noun,noun_index=compute_capitals(line)
    #not_included_index=[]
    for index in noun_index:
        if index not in target_index:
            #not_included_index.append(index)
            for i in range(0,len(target_index)):
                if target_index[i]>index:
                    target_index.insert(i,index)
                    break
    line=line.split()
    target=[]
    for i in range(0,len(target_index)):
        #if target_index[i] not in not_included_index:
        target.append(line[target_index[i]])
    return target,target_index


def compute_POS(line):
    annotator=Annotator()
    pos=annotator.getAnnotations(line)['pos']
    pos_tag=[]
    for p in pos:
        pos_tag.append(p[1])
    return pos_tag


def get_index(list_r,element):
    for i in range(0,len(list_r)):
        if list_r[i]==element:
            return i
    return -1


def extract_target(question):
    POS=compute_POS(question)
    index = []
    target=[]

    for i in range(0,len(POS)):
        if POS[i] in ['NN','NNP','NNS','NNPS','RBS','CD','FW','JJ','JJS','JJR']:
            index.append(i)

    question = question.split()
    for i in index:
        target.append(question[i])
    return target,index


def remove_fine_target(target, fine_class,target_index):
    temp_target = []
    temp_index = []
    for i in range(0,len(target)):
        if target[i]!=fine_class:
            temp_target.append(target[i])
            temp_index.append(target_index[i])
    return temp_target,temp_index


def merge_similar_target(line,target_index):
    pos=compute_POS(line)
    temp_pos=[pos[i][0]+pos[i][1] for i in range(0,len(pos)-1)]
    line = line.split()
    temp_target=[]
    if len(target_index) > 1 :
        current_index=target_index[0]
        flag=0
        for i in range(0,len(target_index)-1):
            if current_index + 1==target_index[i+1] and same_case(line[current_index],line[target_index[i+1]]):
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
        if flag==0:
            temp_target.append(line[current_index])
    else:
        for i in target_index:
            temp_target.append(line[i])
    return temp_target


def extract_auxiliary_words(line,target,target_index):
    line=line.split()
    stop_words = set(stopwords.words('english'))
    partial_filtered = [w for w in line if not w in stop_words]
    cleaned=[c for c in partial_filtered if not c in target]
    for i in range(1,len(cleaned)-1):
        if cleaned[i]!='\'s':
            index=get_index(line,cleaned[i])
            for j in range(0,len(target_index)):
                if target_index[j]>index:
                    target_index.insert(j,index)
                    break
                if target_index[-1]<index:
                    target_index.append(index)
                    break
    temp_target=[]
    for i in target_index:
        temp_target.append(line[i])
    return temp_target,target_index


###########################################################################################################################
"""
file_r = open("questions.txt","r")
file_w = open("target.txt","w")

stop_words = set(stopwords.words('english'))

for line in file_r:
    if not (equal_quote(line)):
        line =quote_preprocess(line)
    coarse_class,fine_class = get_classes(line)
    special_word,line = extract_special_meaning(line)
    line  = preprocess(line)

    target,target_index=extract_target(line)
    target,target_index=refine_capitals(line,target_index)
    target,target_index=extract_auxiliary_words(line,target,target_index)
    target,target_index=remove_fine_target(target,fine_class,target_index)
    target=merge_similar_target(line,target_index)

    if special_word==[]:
        print line," :: \n",target
        for item in target:
            file_w.write("%s, " % item)
        file_w.write("\n")
        #file_w.write(' '.join(str(e) for e in target)+"\n")

    else:
        print line," :: \n",target," Special Words :: ", special_word
        for item in target:
            file_w.write("%s, " % item)
        file_w.write("\t\t\tSpecial Words :: ")
        for item in special_word:
            file_w.write("%s, " % item)
        file_w.write("\n")
        #file_w.write(' '.join(str(e) for e in target)+"\t\t\tSpecial Words ::"+' '.join(str(e) for e in special_word)+"\n")
    print "\n"
file_w.close()
file_r.close()
"""

def get_target(question):
    if not equal_quote(question):
        question =quote_preprocess(question)
    coarse_class,fine_class = get_classes(question)
    special_word,line = extract_special_meaning(question)
    line  = preprocess(line)

    target,target_index=extract_target(line)
    target,target_index=refine_capitals(line,target_index)
    target,target_index=extract_auxiliary_words(line,target,target_index)
    #target,target_index=remove_fine_target(target,fine_class,target_index)
    target=merge_similar_target(line,target_index)

    print question,"\nCoarse : ",coarse_class,"\nFine : ",fine_class," \nTarget : ",target," \nSpecial Words : ", special_word

    return coarse_class,fine_class,target,special_word
