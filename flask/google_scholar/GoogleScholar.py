# -*- coding: utf-8 -*-

import scholarly
import json

def googleScholar(consultaOriginal, numDocRecupera):

    
    lista=[]
    search_query = scholarly.search_pubs_query(consultaOriginal)   
    for i in range(numDocRecupera):   
        try:
            dic = {}
            datos=next(search_query)        
                    
            if 'abstract' in datos.bib:
                dic['abstract'] = datos.bib['abstract']
            
            if 'author' in datos.bib:
                dic['author'] = datos.bib['author']
            
            if 'eprint' in datos.bib:
                dic['eprint'] = datos.bib['eprint']        
            
            if 'title' in datos.bib:
                dic['title'] = datos.bib['title']
            
            if 'url' in datos.bib:
                dic['url'] = datos.bib['url']
            
            if hasattr(datos, 'citedby'):
                dic['citedby'] = str(datos.citedby)
            
            if hasattr(datos, 'id_scholarcitedby'):
                dic['id_scholarcitedby'] = datos.id_scholarcitedby
            
            if hasattr(datos, 'source'):
                dic['source'] = datos.source
           
            if hasattr(datos, 'url_scholarbib'):
                dic['url_scholarbib'] = datos.url_scholarbib
            
            lista.append(dic)
        except StopIteration:
            print('** Error Scholar: StopIteration')
            pass
        
    return lista
    
    
'''
def printFile(nombreFichero):
    
    data = json.loads(open(nombreFichero+".json").read())       
    
    for x in range(len(data)):
        print('*******************************************************')
        print('Paper nº:' + ' ' + str(x))
        print('-------------------------------------------------------')
        print()
        print('Abstract :'+ ' ' + data[x]['abstract'])
        print()
        print('author :'+ ' ' + data[x]['author'])
        print()
        print('eprint :'+ ' ' + data[x]['eprint'])
        print()
        print('title :'+ ' ' + data[x]['title'])
        print()
        print('url :'+ ' ' + data[x]['url'])
        print()
        print('citedby :'+ ' ' + data[x]['citedby'])
        print()
        print('id_scholarcitedby :'+ ' ' + data[x]['id_scholarcitedby'])
        print()
        print('source :'+ ' ' + data[x]['source'])
        print()
        print('url_scholarbib :'+ ' ' + data[x]['url_scholarbib'])                                        
        print()
        print('-------------------------------------------------------')
'''        
