#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import tokenize
from io import BytesIO
import os
import pickle

class ConceptFinder:
    """
    ConceptFinder: Clase para buscar un concepto de una lista de
    conceptos dada.
    """

    def __init__(self, csv_file1=None):
        self.length=0
        self.concepts={}

        # Load CSV file
        if csv_file1:
            self._loadCSV(csv_file1)
    
    def serialize(self, path):
      file = open(path, 'wb')
      pickle.dump(self, file)
      file.close
      print("Serializado")

    def desserialize(path):
      if os.path.exists(path):
        file = open(path, 'rb')
        conceptFinder = pickle.load(file)
        file.close
        return conceptFinder


    def _loadCSV(self, csv_file):
        with open(csv_file) as f:
            base=os.path.basename(csv_file)
            file_name=base.split('.')[0]
            for l in f:
                c=l.split(';')
                if len(c)>1:
                    info=self.tokenizeText(c[0].strip())
                    key=' '.join([a['token'] for a in info])

                    if key in self.concepts:
                        #print('\n', key,'->',c[1].strip())
                        data = self.concepts[key]
                        string_data = file_name+ ': ' + c[1].strip()
                        if not string_data in data:
                            self.concepts[key].append(string_data)  
                    else:
                        self.concepts[key]=[file_name+ ': ' + c[1].strip()]

                    length=len(info)
                    if length>self.length:
                        self.length=length

    def tokenizeText(self, text):
        l=[]
        offset=0
        nline=1
        last=0
        text = text.lower()
        text = text.replace('á','a')
        text = text.replace('é','e')
        text = text.replace('í','i')
        text = text.replace('ó','o')
        text = text.replace('ú','u')
        string = text.encode('utf-8')
        try:
            g = tokenize.tokenize(BytesIO(string).readline)
            for category, token, ini, fin, line in g:
                if category!=tokenize.ENDMARKER and \
                   category!=tokenize.ENCODING  and \
                   category!=tokenize.NEWLINE  and \
                   category!=tokenize.INDENT  and \
                   category!=tokenize.DEDENT:
                    d={'token':token, 'cat':category}
                    if ini[0]!=nline:
                        nline=ini[0]
                        offset=last+offset
                    d['begin']=ini[1]+offset
                    d['end']=fin[1]+offset
                    last=fin[1]+offset
                    l.append(d)
        except tokenize.TokenError as e:
            pass  #Saltar el error de no encontrar el cierre de paréntesis.
        return l

    def search(self, text):
        terms = self.tokenizeText(text)
        total = len(terms)
        result=[]
        for pos,data in enumerate(terms):
            end = min(total-pos,self.length)
            reg={}
            for y in range(0,end):
                l=terms[pos:pos+y+1]
                k=[a['token'] for a in l]
                ini=l[0]['begin']
                fin=l[y]['end']
                key=' '.join(k)
                if key in self.concepts:
                    reg={'begin':ini,'end':fin,'concept':key,'data':self.concepts[key]}

            if 'concept' in reg:
                result.append(reg)

        return result