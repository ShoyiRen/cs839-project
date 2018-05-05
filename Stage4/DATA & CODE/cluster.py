import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.cluster import *
from sklearn.preprocessing import normalize

df = pd.read_csv('TableE.csv')
title_vectorizer = TfidfVectorizer()
title_tfidf = title_vectorizer.fit_transform(df['title'])
author_vectorizer = CountVectorizer()
author_tfidf = author_vectorizer.fit_transform(df['author'])

features = normalize(np.concatenate((title_tfidf.toarray(), author_tfidf.toarray()), axis=1))

num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters).fit(features)
agc = AgglomerativeClustering(n_clusters=num_clusters).fit(features)
birch = Birch(n_clusters=num_clusters).fit(features)

result = []
for i in range(len(df)):
    result.append((str(kmeans.labels_.tolist()[i]) + ': ' + df['title'][i]))

result.sort()

print('\n'.join(result))
print('distortion: ' + str(kmeans.inertia_ / len(df)))

for i in range(num_clusters):
    print('number of cluster #' + str(i) + ': ' + str(kmeans.labels_.tolist().count(i)))

