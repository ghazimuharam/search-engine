import math
from string import punctuation
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from datetime import datetime
import re


class Search():
    """
    Class for searching algorithm
    """
    factory = StemmerFactory()
    stemmer = factory.create_stemmer()
    stopword = StopWordRemoverFactory()
    stopword = stopword.create_stop_word_remover()
    ARTICLE_DIR = './Clean/'

    def __init__(self, inverted_index):
        self.inverted_file = open(inverted_index, 'r')
        self.doc_vector, self.tfidf = self.read_inverted()

    def read_inverted(self):
        """
        Read tf-idf from provided file
        """
        tfidf = {}
        inverted_index = {}
        doc_vector = {}
        for line in self.inverted_file.read().split('\n'):
            splitter = line.split('|')
            term = splitter[0].split('-')
            try:
                tfidf[term[0]] = {'idf': float(term[1].split(':')[1])}
            except IndexError:
                pass

            for docs_tf in splitter[1:]:
                docs_tf = docs_tf.split(':')

                tfidf[term[0]][docs_tf[0]] = float(docs_tf[1])
                if docs_tf[0] not in doc_vector:
                    doc_vector[docs_tf[0]] = float(docs_tf[1])**2
                else:
                    doc_vector[docs_tf[0]] += float(docs_tf[1])**2
        return doc_vector, tfidf

    def text_cleaner(self, text):
        """
        Remove punctuation, stopwords and stemming using 
        PySastrawi module
        """
        content = text.translate(str.maketrans('', '', punctuation))
        content = self.stopword.remove(content)
        text_cleaned = self.stemmer.stem(content.lower())

        query = []

        for token in text_cleaned.split(' '):
            if token not in self.tfidf:
                continue
            else:
                query.append(token)
        return query

    def query_vectorizer(self, query_token):
        """
        Vectorize query and count tfidf for the responsible 
        term
        """
        query_tf = {}
        query_tfidf = {}
        for token in query_token:
            if token not in self.tfidf:
                query_tfidf[token] = 0

            if token not in query_tf:
                query_tf[token] = 1
            else:
                query_tf[token] += 1
        total_sum = sum(query_tf.values())
        for token in query_token:
            if token not in self.tfidf:
                continue
            query_tfidf[token] = float(query_tf[token]) / \
                total_sum * self.tfidf[token]['idf']

        return query_tfidf

    def document_in_query_token(self, query_token):
        """
        return only document related to the query
        """
        union_docs = []
        for token in query_token:
            union_docs.extend(list(self.tfidf[token].keys()))
        if 'idf' in union_docs:
            union_docs.remove('idf')
        union_docs = set(union_docs)

        return union_docs

    def norm_from_vector(self, vector: dict):
        """
        return norm of given vector
        """
        norm = 0
        for key in vector.keys():
            norm += vector[key]**2
        return math.sqrt(norm)

    def search_query(self, query):
        """
        return document sorted by the cosine measure
        for each document
        """

        start = datetime.now()
        query_token = self.text_cleaner(query)
        query_tfidf = self.query_vectorizer(query_token)
        union_docs = self.document_in_query_token(query_token)

        cosine_measure = {}
        for token in query_token:
            for document in union_docs:
                if document not in self.tfidf[token]:
                    cosine_value = 0
                else:
                    cosine_value = self.tfidf[token][document] * \
                        query_tfidf[token]

                if document not in cosine_measure:
                    cosine_measure[document] = cosine_value
                else:
                    cosine_measure[document] += cosine_value
        if 'idf' in cosine_measure:
            cosine_measure.pop('idf')

        for key in cosine_measure.keys():
            cosine_measure[key] /= self.norm_from_vector(
                query_tfidf) * math.sqrt(self.doc_vector[key])
        cosine_measure = dict(
            sorted(cosine_measure.items(), key=lambda item: item[1], reverse=True))

        end = datetime.now()-start
        cosine_measure['process_time'] = end.total_seconds()
        return cosine_measure

    def get_article(self, docs_id):
        """
        return all of article information to display
        on website
        """
        file = open(self.ARTICLE_DIR + docs_id).read()

        article = {}
        url = re.search('(?<=\<url\>).*?(?=\<\/url\>)', file)
        title = re.search('(?<=\<title\>).*?(?=\<\/title\>)', file)
        top = re.search('(?<=\<top\>).*?(?=\<\/top\>)', file)
        middle = re.search('(?<=\<middle\>).*?(?=\<\/middle\>)', file)
        bottom = re.search('(?<=\<bottom\>).*?(?=\<\/bottom\>)', file)

        article['url'] = url[0]
        article['title'] = title[0]
        isi = top[0] + middle[0] + bottom[0]
        if len(isi) > 200:
            article['text'] = isi[:200] + '...'
        else:
            article['text'] = isi

        return article
