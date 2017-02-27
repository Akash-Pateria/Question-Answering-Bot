import re
import nltk
from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import hstack
from sklearn.svm import LinearSVC
from practnlptools.tools import Annotator
from readproperties import read_property
import cPickle

##removing special characters from sentence##
def preprocess(raw_sentence):
    sentence= re.sub(r'[$|.|!|"|(|)|,|;|`|\']',r'',raw_sentence)
    return sentence

##making the file format ready to use##
def file_preprocess(filename):
    corpus=[]
    classes=[]
    f=open(filename,'r')
    lines=f.readlines()
    for line in lines:
        line=line.rstrip('\n')
        if not (line=="\n"):
            classes.append((line.split()[0]).split(":")[0])
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

#appending features from filename
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


######################################TRAINING############################################

#######Train class labels#####
train_class=[]
f=open(read_property('trainingfilepath'),'r')
lines=f.readlines()
for line in lines:
    line=line.rstrip('\n')
    if not (line=="\n"):
        train_class.append((line.split()[0]).split(":")[0])


print ("Training")

vectorizer_words= CountVectorizer(min_df=1,ngram_range=(1, 2))
X_words = vectorizer_words.fit_transform(append('word_features_train_coarse_path'))
f.close()
print ("word feature extraction done")


vectorizer_POS= CountVectorizer(min_df=1,ngram_range=(1, 2))
X_POS = vectorizer_POS.fit_transform((append('POS_features_train_coarse_path')))
f.close()
print ("POS feature extraction done")


vectorizer_Chunk= CountVectorizer(min_df=1,ngram_range=(1, 2))
X_Chunk = vectorizer_Chunk.fit_transform((append('Chunk_features_train_path')))
f.close()
print ("Chunk feature extraction done")


vectorizer_NER= CountVectorizer(min_df=1,ngram_range=(1, 2))
X_NER = vectorizer_NER.fit_transform(append('NER_features_train_coarse_path'))
f.close()
print ("Vectorize")
print ("NER feature extraction done")


X=hstack((X_words,X_POS))
X_train=hstack((X,X_NER))
X_train=hstack((X_train,X_Chunk))


######################################TESTING############################################

print ("In Testing")

filename_test=read_property('testfilepath')
corpus_test,test_class_gold=file_preprocess(filename_test)

#vectorizer_words= CountVectorizer(min_df=1)
X_words = vectorizer_words.transform((append('word_features_test_coarse_path')))
f.close()
print ("word feature test extraction done")

#vectorizer_POS= CountVectorizer(min_df=1)
X_POS = vectorizer_POS.transform((append('POS_features_test_coarse_path')))
f.close()
print ("POS feature test extraction done")

#vectorizer_Chunk= CountVectorizer(min_df=1)
X_Chunk = vectorizer_Chunk.transform((append('Chunk_features_test_path')))
f.close()
print ("Chunk feature test extraction done")

#vectorizer_NER= CountVectorizer(stop_words=None,min_df=1)
X_NER = vectorizer_NER.transform((append('NER_features_test_coarse_path')))
f.close()
#print ("Vectorize")
print ("NER feature test extraction done")


X=hstack((X_words,X_POS))
X_test=hstack((X,X_NER))
X_test=hstack((X_test,X_Chunk))


###################Applying the LinearSVC Classifier#########################

print ("Applying SVC")
coarse_model = LinearSVC(loss='squared_hinge', dual=False, tol=1e-3)
coarse_model = LinearSVC.fit(coarse_model, X_train, train_class)
test_class = LinearSVC.predict(coarse_model, X_test)

'''
Saving the model in secondory memory for future references
'''
pickle_out = open("TrainedModels/coarse_model.pickle","wb")
cPickle.dump(coarse_model, pickle_out, protocol=cPickle.HIGHEST_PROTOCOL)

''' storing to secondory memory done '''


#####Calculating success rate#####
hits=0.00
fi=open(read_property('coarse_classification_path'),"w")
for i in range(0,len(test_class)):
    str_l=test_class[i]," : ",corpus_test[i],"\n"
    fi.write(test_class[i]+" : ")
    fi.write(corpus_test[i]+"\n")
fi.close()

for i in range(0,len(test_class)):
	if test_class[i]==test_class_gold[i]:
		hits=hits+1
print ("Number of hits = ",hits)
print ("The accuracy is ",((hits/len(test_class))*100.0)," %")
print ("Total test Case : ",len(test_class))
