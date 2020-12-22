from pathlib import Path
from tqdm import tqdm
import re
import sys
import math
import json

files = Path().cwd().glob("./Documents/Clean/*/*.html")

total_file = 0


def get_text(file, tag):
    return re.search(f'<{tag}>(.*?)</{tag}>', file).group(1)


def indexer(hashs, terms):
    for term in terms:
        if term in hashs:
            hashs[term] += 1
        else:
            hashs[term] = 1


tf, df = {}, {}

for file in sorted(files):
    filename = file.name
    df[filename] = {}

    file = open(file, 'r')
    file = file.read()

    terms = (get_text(file, 'title') + ' ' + get_text(file, 'top') +
             ' ' + get_text(file, 'middle') + ' ' + get_text(file, 'bottom')).split()

    indexer(df[filename], terms)
    indexer(tf, terms)

    total_file += 1
    if total_file == 3000:
        break


def calculate_idf():
    idf = {}
    for term in tf:
        total_doc = 0
        for doc_id in df:
            if term in df[doc_id]:
                total_doc += 1
        try:
            idf_doc = math.log2(len(df)/total_doc)
        except:
            idf_doc = 0
        idf[term] = idf_doc
    return idf


# inverted_index = {}
idf = calculate_idf()

total_iter = 0
with open('term_tfidf.txt', 'w') as file:
    for term, term_freq in tqdm(tf.items()):
        file.write('{}-idf:{}'.format(term, idf[term]))
        total_iter += 1
        for doc_id in df.keys():
            doc_tf = 0
            total_term = 0
            if term in df[doc_id]:
                doc_tf = df[doc_id][term]
            total_term += sum(df[doc_id].values())
            term_frequency = doc_tf / total_term
            tfidf = term_frequency * idf[term]

            if tfidf > 0:
                file.write(f'|%s:%.3f' % (doc_id, tfidf))
        file.write('\n')
