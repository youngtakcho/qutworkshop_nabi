import json
import sklearn
import sqlite3
from gensim.models import word2vec , doc2vec
import gensim
import pickle
from gensim.parsing import *
from gensim.similarities.docsim import SparseMatrixSimilarity ,Similarity


def preprocess(text):
    CUSTOM_FILTERS = [lambda x: x.lower(), strip_tags, strip_punctuation,stem_text,remove_stopwords,strip_multiple_whitespaces,strip_short]
    return gensim.parsing.preprocess_string(text,CUSTOM_FILTERS)

dictionary:gensim.corpora.Dictionary = gensim.corpora.Dictionary.load("./dictionary.gensim")
data = None
with open('dictionary.pickle', 'rb') as handle:
    data = pickle.load(handle)


query = "small character good music bright background"
query_arr = preprocess(query)
dictionary.add_documents([query_arr])
bow_q = dictionary.doc2bow(query_arr)

results:set = data[query_arr[0]]
for i in query_arr[1:]:
    results = results.intersection(data[i])

conn = sqlite3.connect("game_data copy 3.db")
c = conn.cursor()
q = "SELECT r_id,text from reviews WHERE r_id IN " + str(tuple(results)) +""
c.execute(q)
rows = c.fetchall()

bows = []
indices = []
for idx,review in rows:
    pre = preprocess(review)
    bow = dictionary.doc2bow(pre)
    bows.append(bow)
    indices.append(idx)

model = gensim.models.TfidfModel(bows)
siml = Similarity(None,bows,num_features=len(dictionary))
result_siml = siml[bow_q]
ordered = sorted(range(len(result_siml)), key=lambda k: result_siml[k])
for i in ordered:
    print(indices[i])