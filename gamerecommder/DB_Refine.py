import sklearn
import sqlite3
from gensim.models import word2vec , doc2vec , tfidfmodel
import gensim
from gensim.parsing import *
import pickle

def preprocess(text):
    CUSTOM_FILTERS = [lambda x: x.lower(), strip_tags, strip_punctuation,stem_text,remove_stopwords,strip_multiple_whitespaces,strip_short]
    return gensim.parsing.preprocess_string(text,CUSTOM_FILTERS)

# dictionary = gensim.corpora.Dictionary()

dictionary:gensim.corpora.Dictionary = gensim.corpora.Dictionary.load("./dictionary.gensim")
conn = sqlite3.connect("game_data copy 3.db")
c = conn.cursor()
c.execute("select r_id , text from reviews")
rows = c.fetchall()

documents = []
size = len(rows)
index = 0

for (idx, text) in rows:
    q = conn.cursor()
    if len(text) < 1:
        continue
    sentence = text.lower()
    r = preprocess(sentence)
    corpus = dictionary.doc2bow(r)
    documents.append(corpus)
    index += 1
    query = "INSERT INTO corpus (r_id,corp)"
    val = str(corpus)
    query += " VALUES ("+str(idx)+",\""+val+"\""+")"
    q.execute(query)
    if index / size * 100 % 10 <= 0.1:
        print(index / size * 100, "%")

conn.commit()

# dictionary.save("./dictionary.gensim")


# model = doc2vec.Doc2Vec(documents=result, size=100, window=5, min_count=5, workers=4, sg=0)
# model = word2vec.Word2Vec(sentences=result, size=50000, window=5, min_count=5, workers=4, sg=0)
# model.save("test.model")



