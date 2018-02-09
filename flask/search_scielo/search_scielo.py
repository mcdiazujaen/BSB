import sys
import os
import json
import string
import re
from datetime import datetime, date, time, timedelta
sys.path.append('/usr/share')
from elasticsearch import Elasticsearch

def getListStopWord(path):
    f = open(path, 'r')
    content = f.readlines()
    list_stop_word = [x.strip() for x in content] 
    return list_stop_word

def wordInStopper(word, list_stop_word):
    word = word.replace('<em>', '')
    word = word.replace('</em>', '')
    transtable = str.maketrans('', '', string.punctuation)
    word = word.translate(transtable)
    return word.lower() in list_stop_word

def cleanStopWord(text):
    myPath= os.getcwd()
    list_stop_word = getListStopWord( myPath.strip() +'/search_scielo/stop_word.txt')

    list_text = text.split()
    new_text = ''
    for word in list_text:
        if "<em>" in word and "</em>" in word:
            new_word = word.replace("<em>", "")
            new_word = new_word.replace("</em>", "")
            if wordInStopper(new_word, list_stop_word) == True:
                new_text += ' ' + new_word
            else:
                new_text += ' ' + word
        else:
            new_text += ' ' + word

    return new_text

def getSnippetsHighlight(text):
    list_text = text.split()
    snippet = '...'
    last = 0
    add = 0
    for index, word in enumerate(list_text):
        if add == 4:
            break
        if '<em>' in word and index > last:
            if index >= 10 and len(list_text) >= index+11:
                snippet += ' '.join(list_text[index - 10: index + 11])
                snippet += '...'
                last = index + 10
                add = add + 1
            elif index < 10 and len(list_text) >= index+11:
                snippet += ' '.join(list_text[index: index + 11])
                snippet += '...'
                last = index + 10
                add = add + 1
            elif index  >= 10 and len(list_text) < index+11:
                snippet += ' '.join(list_text[index - 10: len(list_text)])
                last = len(list_text)
                add = add + 1

    snippet = snippet.replace('......', '...')
    snippet = snippet.replace("<em>", "<b>")
    snippet = snippet.replace("</em>", "</b>")
    return snippet

def getHighlight(text):
    ini = text.find('<em>')
    text = text[ini:]
    list_text = text.split()
    text = ' '.join(list_text[0:75])
    text = text.replace("<em>", "<b>")
    text = text.replace("</em>", "</b>")
    text += '...'
    return text

#---------------------------------------------------------
# Función que ejecuta la query en el índice indicado

def run_query ( es, index_name, terms, num_doc ): 
    list_scielo = []
    highlight = '"highlight" : { "fields" : { "title" : { "number_of_fragments": 0, "fragment_size" : 150 }, "text": {"number_of_fragments":0, "fragment_size" : 150 }}}'

    query = '{ "sort" : ["_score"], "query":{"match":{"text":"'+terms+'"}}, '+highlight+'}'
    #Simple Elasticsearch Query
    res = es.search(index=index_name, body=query)
    
    for index, doc in enumerate(res['hits']['hits']):
        if index >= int(num_doc):
            break

        id = doc['_id']
        url = 'http://scielo.isciii.es/scielo.php?script=sci_arttext&pid=' + doc['_id']
        title = doc['_source']['title']
        text =  doc['highlight']['text'][0]
        text = cleanStopWord(text)
        text = getSnippetsHighlight(text)

        dic = {'id': id, 'url': url, 'text' :text, 'title' : title}
        list_scielo.append(dic)
    return list_scielo

#---------------------------------------------------------

def search(terms, num_doc):

    index_name = 'scielo_title'
    es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

    list_result = []

    if not index_name is None and not terms is None:
        list_term = terms.split()
        while(len(list_term) > 0):
            query = ' '.join(list_term)
            list_result = run_query(es, index_name, terms, num_doc)

            if len(list_result) > 0:
                return list_result
            else:
                del list_term[-1]

    return list_result
