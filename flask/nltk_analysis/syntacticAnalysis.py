#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import tokenize
import re
import nltk.data
from nltk.tokenize import WordPunctTokenizer
from nltk.tag import StanfordPOSTagger

class SyntacticAnalysis(): 

	def searchDiccionariesPositions(begin, end , list_of_dictionaries):
		return [element for element in list_of_dictionaries if element['begin'] == begin and element['end'] == end]

	def getLisNouns(list_postagger, list_ner):
		new_list_ner = []
		for entity in list_ner:
			begin = entity['begin']
			end = entity['end']
			concept = entity['concept']
			if len(concept.split()) > 1:
				new_list_ner.append(entity)
			else:
				element_postagger = SyntacticAnalysis.searchDiccionariesPositions(begin, end, list_postagger)
				if len(element_postagger) == 1:
					if re.match('n.*|a.*|z.*', element_postagger[0]['tag']):
						new_list_ner.append(entity)
		return new_list_ner

	def getLisNoVerb(list_postagger, list_ner):
		new_list_ner = []
		for entity in list_ner:
			begin = entity['begin']
			end = entity['end']
			concept = entity['concept']
			if len(concept.split()) > 1:
				new_list_ner.append(entity)
			else:
				element_postagger = SyntacticAnalysis.searchDiccionariesPositions(begin, end, list_postagger)
				if len(element_postagger) == 1:
					if not re.match('v.*', element_postagger[0]['tag']):
						new_list_ner.append(entity)
		return new_list_ner

	def analysisSpa(text):
		list_postagger = []
		list_text = text.split(' ')
		"""Analisis sintactico"""
		myPath = os.getcwd()

		os.environ['CLASSPATH'] = myPath.strip() +'/nltk_analysis/stanford-postagger-full-2017-06-09'.strip()
		os.environ['STANFORD_MODELS'] = myPath.strip() +'/nltk_analysis/stanford-postagger-full-2017-06-09/models/'.strip()
		
		pathTagger =  myPath.strip() +"/nltk_analysis/stanford-postagger-full-2017-06-09/models/spanish.tagger".strip()
		spanishTagger = nltk.tag.stanford.StanfordPOSTagger(pathTagger, encoding='utf8')

		tokenizer = WordPunctTokenizer()
		tags = spanishTagger.tag(tokenizer.tokenize(text))
		
		list_postagger = []
		offset, length = 0, 0
		for sentence, tag in tags:
		    # fix ignored characters
		    while text[offset] != sentence[0]:
		        offset += 1

		    length = len(sentence)
		    dic = {'concept': sentence, 'begin': offset, 'end': offset+length, 'tag': tag}
		    list_postagger.append(dic)
		    offset += length

		return list_postagger


