from sklearn.feature_extraction.text import CountVectorizer
from scipy.sparse import hstack
from sklearn.svm import LinearSVC
from practnlptools.tools import Annotator
import cPickle
from fine_class_fullname import read_class


annotator=Annotator()

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

def get_classes(question):

    ''' loading the coarse model '''
    pickle_in_coarse = open("../classifier/TrainedModels/coarse_model.pickle","rb")
    coarse_model = cPickle.load(pickle_in_coarse)
    pickle_in_coarse.close()

    '''loading vectorizer for coarse model '''

    pickle_in = open("../classifier/TrainedModels/"+"coarse_vectorizer_words.pickle","rb")
    vectorizer_words = cPickle.load(pickle_in)
    pickle_in = open("../classifier/TrainedModels/"+"coarse_vectorizer_POS.pickle","rb")
    vectorizer_POS = cPickle.load(pickle_in)
    pickle_in = open("../classifier/TrainedModels/"+"coarse_vectorizer_NER.pickle","rb")
    vectorizer_NER = cPickle.load(pickle_in)
    pickle_in = open("../classifier/TrainedModels/"+"coarse_vectorizer_Chunk.pickle","rb")
    vectorizer_Chunk = cPickle.load(pickle_in)

    X_words = compute_word(question,vectorizer_words)
    X_POS = compute_POS(question,vectorizer_POS)
    X_NER = compute_NER(question,vectorizer_NER)
    X_Chunk = compute_Chunk(question,vectorizer_Chunk)

    pickle_in.close()

    X=hstack((X_words,X_POS))
    X_coarse=hstack((X,X_NER))
    X_coarse=hstack((X_coarse,X_Chunk))

    coarse_class = LinearSVC.predict(coarse_model,X_coarse)

    '''
    Getting the coarse class output in string form
    '''
    coarse_class = coarse_class[0]

    ''' loading the fine model as per the prediction of the coarse model '''
    pickle_in_fine = open("../classifier/TrainedModels/"+coarse_class+"_model.pickle","rb")
    fine_model = cPickle.load(pickle_in_fine)
    pickle_in_fine.close()

    '''loading vectorizer for fine model depending on the coarse output '''

    pickle_in = open("../classifier/TrainedModels/"+coarse_class+"_vectorizer_words.pickle","rb")
    vectorizer_words = cPickle.load(pickle_in)
    pickle_in = open("../classifier/TrainedModels/"+coarse_class+"_vectorizer_POS.pickle","rb")
    vectorizer_POS = cPickle.load(pickle_in)
    pickle_in = open("../classifier/TrainedModels/"+coarse_class+"_vectorizer_NER.pickle","rb")
    vectorizer_NER = cPickle.load(pickle_in)
    pickle_in = open("../classifier/TrainedModels/"+coarse_class+"_vectorizer_Chunk.pickle","rb")
    vectorizer_Chunk = cPickle.load(pickle_in)

    X_words = compute_word(question,vectorizer_words)
    X_POS = compute_POS(question,vectorizer_POS)
    X_NER = compute_NER(question,vectorizer_NER)
    X_Chunk = compute_Chunk(question,vectorizer_Chunk)

    pickle_in.close()

    X=hstack((X_words,X_POS))
    X_fine=hstack((X,X_NER))
    X_fine=hstack((X_fine,X_Chunk))

    fine_class = LinearSVC.predict(fine_model,X_fine)

    '''
    Getting the fine class output in string form
    '''
    fine_class = fine_class[0]

    '''
    Get the proper name of the fine class
    '''
    fine_class = read_class(fine_class)

    return coarse_class,fine_class
'''
End of get_classes function
'''
