import re
import requests
import xml.etree.ElementTree as ET
import operator


def cleanHtml(text_html):
  text_html = text_html.replace('&lt;', '<')
  text_html = text_html.replace('&gt;' , '>')
  #cleanr = re.compile('<.*?>')
  text_html = text_html.replace('<span class="qt0">', '<b>')
  text_html = text_html.replace('</span>' , '</b>')
  #text_html = re.sub(cleanr, '', text_html)
  text_html = text_html.replace('\n', '')
  text_html = text_html.replace('\t', '')
  text_html = " ".join(text_html.split())
  return text_html

def obtain_list_medliplus(xml, num_doc):
    tree = ET.ElementTree(ET.fromstring(xml))
    root = tree.getroot()
    
    list_articles = []
    
    count = root.find('count').text
    #print(count)
    
    if int(count) > 0 :
        for document in root.iter('document'):
            dic = {}
            if int(count) > int(num_doc):
                dic['rank'] = int(num_doc)-int(document.get('rank'))
            else:
                dic['rank'] = int(count)-int(document.get('rank'))
                
            dic['url'] = document.get('url')
                        
            for content in document.findall('content'):
                if content.get('name') == 'title':
                    text = cleanHtml(ET.tostring(content, encoding='unicode'))
                    dic['title'] = text
                
                if content.get('name') == 'organizationName':
                    text = cleanHtml(ET.tostring(content, encoding='unicode'))
                    dic['organizationName'] = text
                
                if content.get('name') == 'snippet':
                    text = cleanHtml(ET.tostring(content, encoding='unicode'))
                    dic['snippet'] = text
                
                
            list_articles.append(dic)
    return list_articles

def ws_medlineplus_spanish(text, num_doc):
    query = text.replace(' ', '+')
    url ="https://wsearch.nlm.nih.gov/ws/query?db=healthTopicsSpanish&term="+ query+ '&retmax=' + str(num_doc)
    r = requests.get(url)
    if not r.text is None:
        r.encoding = 'utf-8'
        xml = r.text
        list_articles = obtain_list_medliplus(xml, num_doc)
    
    return list_articles

def searchDictionaries(key, value, list_of_dictionaries):
    return next((element for element in list_of_dictionaries if element[key] == value), False)

def search (list_ner, num_doc):
    list_final = []
    for entity in list_ner:
        dic_arct = [] 
        list_articles = ws_medlineplus_spanish(entity, num_doc)
        
        if len(list_articles) > 0:
            for article in list_articles:
                dic_arct.append({'key' : article['url'], 'rank' : article['rank'], 'title' : article['title'], 'organizationName': article['organizationName'], 'snippet': article['snippet'] })
        list_final.append(dic_arct)
    return orderDoc(list_final, num_doc)


def orderDoc(list_final,num_doc):
    new_list = []
    for index1, dic1 in enumerate(list_final):
        for doc1 in dic1:
            #print('\nLeemos: ', doc1)
            if not searchDictionaries('key', doc1['key'], new_list):
                repetido = False
                rank = int(doc1['rank'])
                for dic2 in list_final[index1+1:]:
                    for doc2 in dic2:
                        if doc1['key'] == doc2['key']:
                            #print('\tSI    ', doc2)
                            repetido = True
                            rank += int(doc2['rank'])
                        #else:
                            #print('\tNO    ', doc2)
                    
                if repetido:
                    rank = rank/len(list_final)
                else:
                    rank = rank/len(list_final)
                #print('añadimos: ', doc1['key'] , 'rank : ', rank)
                new_list.append( {'key': doc1['key'] , 'rank': rank , 'title' : doc1['title'], 'organizationName': doc1['organizationName'], 'snippet': doc1['snippet'] })
            #else:
                #print('no añadimos: ', doc1['key'])
                    
    new_list.sort(key=operator.itemgetter('rank'), reverse=True)
    return new_list[:num_doc]

#list_ner = ['edema pulmonar', 'insuficiencia cardíaca congestiva', 'pulmonar']
#print(search(list_ner, 5))
                
