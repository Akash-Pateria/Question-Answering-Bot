import re
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import hstack
from sklearn.svm import LinearSVC
from practnlptools.tools import Annotator
from readproperties import read_property
import cPickle


annotator=Annotator()

def preprocess(raw_sentence):
    sentence= re.sub(r'[$|.|!|"|(|)|,|;|`|\']',r'',raw_sentence)
    return sentence

def append(filename):
	f=open(read_property(filename),"r")
	corpus=[]
	for lines in f:
		l=lines.split()
		words=""
		for w in l:
			words=words+w+" "
		corpus.append(words)
	return corpus

def append_noread(filename):
	f=open(filename,"r")
	corpus=[]
	for lines in f:
		l=lines.split()
		words=""
		for w in l:
			words=words+w+" "
		corpus.append(words)
	return corpus


def file_preprocess(filename):
    corpus=[]
    classes=[]
    superclass=[]
    f=open(filename,'r')
    lines=f.readlines()
    for line in lines:
        line=line.rstrip('\n')
        if not (line=="\n"):
            classes.append((line.split()[1]).split(":")[1])
            superclass.append((line.split()[1]).split(":")[1])
    for line in lines:
        line=line.rstrip('\n')
        line=preprocess(line)
        sentence=""
        words=line.split()
        for i in range(0,len(words)):
            if not(i==0):
                sentence=sentence+(words[i])+" "
        corpus.append(sentence)
    f.close()
    return corpus,superclass,classes

def file_preprocess_test(filename):
    corpus=[]
    classes=[]
    f=open(filename,'r')
    lines=f.readlines()
    for line in lines:
        line=line.rstrip('\n')
        if not (line=="\n"):
            classes.append((line.split()[0]).split(":")[1])
    for line in lines:
        line=line.rstrip('\n')
        line=preprocess(line)
        sentence=""
        words=line.split()
        for i in range(0,len(words)):
            if not(i==0):
                sentence=sentence+(words[i])+" "
        corpus.append(sentence)
    f.close()
    return corpus,classes

def get_coarse_output_class():
    corpus=[]
    classes=[]
    f=open('CoarseOutputfiles/coarse_classification.txt','r')
    lines=f.readlines()
    for line in lines:
        line=line.rstrip('\n')
        if not (line=="\n"):
            classes.append((line.split()[0]))
    f.close()
    return classes

pickle_in = open("TrainedModels/NUM_model.pickle","rb")
NUM_model = cPickle.load(pickle_in)

pickle_in = open("TrainedModels/LOC_model.pickle","rb")
LOC_model = cPickle.load(pickle_in)

pickle_in = open("TrainedModels/ENTY_model.pickle","rb")
ENTY_model = cPickle.load(pickle_in)

pickle_in = open("TrainedModels/HUM_model.pickle","rb")
HUM_model = cPickle.load(pickle_in)

pickle_in = open("TrainedModels/DESC_model.pickle","rb")
DESC_model = cPickle.load(pickle_in)

pickle_in = open("TrainedModels/ABBR_model.pickle","rb")
ABBR_model = cPickle.load(pickle_in)




coarse_class = get_coarse_output_class()
coarse_corpus = []
f=open('TestOutputfiles/word_features_test.txt','r')
lines=f.readlines()
for line in lines:
    line=line.rstrip('\n')
    if not (line=="\n"):
        coarse_corpus.append(line)
f.close()


filename_test=read_property('testfilepath')
corpus_test,test_class_gold=file_preprocess_test(filename_test)



def compute_word(line,v):
    corpus=[]
    words=""
    l=line.split()
    for w in l:
    	words=words+w+" "
    corpus.append(words)
    X_words = v.transform(corpus)
    return X_words

def compute_POS(line,v):
    corpus=[]
    text = nltk.word_tokenize(line)
    pos_seq=nltk.pos_tag(text)
    pos_tags=""
    for pos in pos_seq:
    	pos_tags=pos_tags+pos[1]+" "
    corpus.append(pos_tags)
    X_POS = v.transform(corpus)
    return X_POS

def compute_NER(line,v):
    corpus=[]
    ner=annotator.getAnnotations(line)['ner']
    ner_tag=""
    for n in ner:
    	ner_tag=ner_tag+n[1]+" "
    corpus.append(ner_tag)
    X_NER= v.transform(corpus)
    return X_NER

def compute_Chunk(line,v):
    corpus=[]
    chunks=annotator.getAnnotations(line)['chunk']
    chunk=""
    for elem in chunks:
    	chunk=chunk+elem[1]+" "
    corpus.append(chunk)
    X_Chunk= v.transform(corpus)
    return X_Chunk


test_class_gold=[]
f=open(read_property('testfilepath'),'r')
for lines in f:
	test_class_gold.append(lines.split()[0].split(':')[1])


hits = 0.00
print ("Testing ..........(it may take some time) ")
for i in range(0,len(coarse_class)):
    file_word=read_property('FineOutputfilesPath')+coarse_class[i]+"_training_word.txt"
    file_POS=read_property('FineOutputfilesPath')+coarse_class[i]+"_training_POS.txt"
    file_NER=read_property('FineOutputfilesPath')+coarse_class[i]+"_training_NER.txt"
    file_Chunk=read_property('FineOutputfilesPath')+coarse_class[i]+"_training_Chunk.txt"

    vectorizer_words= CountVectorizer(min_df=1,ngram_range=(1, 2))
    vectorizer_POS= CountVectorizer(min_df=1,ngram_range=(1, 2))
    vectorizer_Chunk= CountVectorizer(min_df=1,ngram_range=(1, 2))
    vectorizer_NER= CountVectorizer(min_df=1,ngram_range=(1, 2))

    vectorizer_words.fit_transform(append_noread(file_word))
    vectorizer_POS.fit_transform(append_noread(file_POS))
    vectorizer_NER.fit_transform(append_noread(file_NER))
    vectorizer_Chunk.fit_transform(append_noread(file_Chunk))

    X_words = compute_word(coarse_corpus[i],vectorizer_words)
    X_POS = compute_POS(coarse_corpus[i],vectorizer_POS)
    X_NER = compute_NER(coarse_corpus[i],vectorizer_NER)
    X_Chunk = compute_Chunk(coarse_corpus[i],vectorizer_Chunk)

    X=hstack((X_words,X_POS))
    X_test=hstack((X,X_NER))
    X_test=hstack((X_test,X_Chunk))

    if coarse_class[i]=='NUM':
        test_class = LinearSVC.predict(NUM_model,X_test)
    elif coarse_class[i]=='LOC':
        test_class = LinearSVC.predict(LOC_model,X_test)
    elif coarse_class[i]=='ENTY':
        test_class = LinearSVC.predict(ENTY_model,X_test)
    elif coarse_class[i]=='DESC':
        test_class = LinearSVC.predict(DESC_model,X_test)
    elif coarse_class[i]=='HUM':
        test_class = LinearSVC.predict(HUM_model,X_test)
    elif coarse_class[i]=='ABBR':
        test_class = LinearSVC.predict(ABBR_model,X_test)
    else:
        print ("ERROR")

    if test_class == test_class_gold[i]:
        hits = hits + 1.0

print "Number of hits = ",hits
print "Total cases : ",len(test_class_gold)
print "The accuracy is ",((hits/len(test_class_gold))*100.0)," %"
