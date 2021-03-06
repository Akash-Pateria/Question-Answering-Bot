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


def fine_train_label(label):
    file_label=read_property('FineInputFiles')+label+"_training.txt"
    train_corpus,temp,train_class=file_preprocess(file_label)

    file_word=read_property('FineOutputfilesPath')+label+"_training_word.txt"
    file_POS=read_property('FineOutputfilesPath')+label+"_training_POS.txt"
    file_NER=read_property('FineOutputfilesPath')+label+"_training_NER.txt"
    file_Chunk=read_property('FineOutputfilesPath')+label+"_training_Chunk.txt"

    vectorizer_words= CountVectorizer(min_df=1,ngram_range=(1, 2))
    vectorizer_POS= CountVectorizer(min_df=1,ngram_range=(1, 2))
    vectorizer_Chunk= CountVectorizer(min_df=1,ngram_range=(1, 2))
    vectorizer_NER= CountVectorizer(min_df=1,ngram_range=(1, 2))

    X_words = vectorizer_words.fit_transform(append_noread(file_word))
    X_POS = vectorizer_POS.fit_transform(append_noread(file_POS))
    X_NER = vectorizer_NER.fit_transform(append_noread(file_NER))
    X_Chunk = vectorizer_Chunk.fit_transform(append_noread(file_Chunk))

    X=hstack((X_words,X_POS))
    X_train=hstack((X,X_NER))
    X_train=hstack((X_train,X_Chunk))

    '''saving the vectorizers to secondory memory '''
    pickle_out = open("TrainedModels/"+label+"_vectorizer_words.pickle","wb")
    cPickle.dump(vectorizer_words, pickle_out, protocol=cPickle.HIGHEST_PROTOCOL)
    pickle_out = open("TrainedModels/"+label+"_vectorizer_POS.pickle","wb")
    cPickle.dump(vectorizer_POS, pickle_out, protocol=cPickle.HIGHEST_PROTOCOL)
    pickle_out = open("TrainedModels/"+label+"_vectorizer_NER.pickle","wb")
    cPickle.dump(vectorizer_NER, pickle_out, protocol=cPickle.HIGHEST_PROTOCOL)
    pickle_out = open("TrainedModels/"+label+"_vectorizer_Chunk.pickle","wb")
    cPickle.dump(vectorizer_Chunk, pickle_out, protocol=cPickle.HIGHEST_PROTOCOL)
    ''' storing done '''

    print "Applying SVC"
    label_model = LinearSVC(loss='squared_hinge', dual=False, tol=1e-3)
    label_model = LinearSVC.fit(label_model, X_train, train_class)
    print(label, " training done")

    return label_model

''' End of def fine_train_label '''



'''
Training the model for each coarse class so as the predict the sub_classes
'''
NUM_model=fine_train_label('NUM')
LOC_model=fine_train_label('LOC')
ENTY_model=fine_train_label('ENTY')
HUM_model=fine_train_label('HUM')
DESC_model=fine_train_label('DESC')
ABBR_model=fine_train_label('ABBR')

'''
Saving all the models to secondory memory
'''
pickle_out = open("TrainedModels/NUM_model.pickle","wb")
cPickle.dump(NUM_model, pickle_out, protocol=cPickle.HIGHEST_PROTOCOL)

pickle_out = open("TrainedModels/LOC_model.pickle","wb")
cPickle.dump(LOC_model, pickle_out, protocol=cPickle.HIGHEST_PROTOCOL)

pickle_out = open("TrainedModels/ENTY_model.pickle","wb")
cPickle.dump(ENTY_model, pickle_out, protocol=cPickle.HIGHEST_PROTOCOL)

pickle_out = open("TrainedModels/HUM_model.pickle","wb")
cPickle.dump(HUM_model, pickle_out, protocol=cPickle.HIGHEST_PROTOCOL)

pickle_out = open("TrainedModels/DESC_model.pickle","wb")
cPickle.dump(DESC_model, pickle_out, protocol=cPickle.HIGHEST_PROTOCOL)

pickle_out = open("TrainedModels/ABBR_model.pickle","wb")
cPickle.dump(ABBR_model, pickle_out, protocol=cPickle.HIGHEST_PROTOCOL)

''' storing to secondory memory done '''




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
    pos_seq=annotator.getAnnotations(line)['pos']
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

    pickle_in = open("TrainedModels/"+coarse_class[i]+"_vectorizer_words.pickle","rb")
    vectorizer_words = cPickle.load(pickle_in)
    pickle_in = open("TrainedModels/"+coarse_class[i]+"_vectorizer_POS.pickle","rb")
    vectorizer_POS = cPickle.load(pickle_in)
    pickle_in = open("TrainedModels/"+coarse_class[i]+"_vectorizer_NER.pickle","rb")
    vectorizer_NER = cPickle.load(pickle_in)
    pickle_in = open("TrainedModels/"+coarse_class[i]+"_vectorizer_Chunk.pickle","rb")
    vectorizer_Chunk = cPickle.load(pickle_in)

    X_words = compute_word(coarse_corpus[i],vectorizer_words)
    X_POS = compute_POS(coarse_corpus[i],vectorizer_POS)
    X_NER = compute_NER(coarse_corpus[i],vectorizer_NER)
    X_Chunk = compute_Chunk(coarse_corpus[i],vectorizer_Chunk)

    pickle_in.close()

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
