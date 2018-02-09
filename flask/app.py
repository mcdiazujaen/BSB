#!/usr/bin/env python
# -*- coding: utf-8 -*-

#Modificado todo para utilizar Python 3

from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
import json
import urllib
import base64
import re
import os
from search_entities.conceptfinder import ConceptFinder
from google_scholar import GoogleScholar
from search_ws_medlineplus import ws_medliplus
from search_freeling_med import freeling_med
from search_scielo import search_scielo
from nltk_analysis.syntacticAnalysis import SyntacticAnalysis
from search_entities.searchCUIS import SearchCUIS
from graph import graph

app = Flask(__name__)

#
# Activación/desactivación de módulos
# (para acelerar las pruebas)
#

ENABLE_SEARCH = True
ENABLE_SCHOLAR = False
ENABLE_MEDLINE = True
ENABLE_SCIELO = True
ENABLE_GRAPH = False

#
# Carga de datos
#

if ENABLE_SEARCH:
  if os.path.exists('./data/serialize.dat'):
    conceptFinder = ConceptFinder.desserialize('./data/serialize.dat')
    print('Cargados los diccionarios.')

  else:
    file = './data/UMLS_concept.txt'
    conceptFinder = ConceptFinder(file)
    file = './data/Medline.txt'
    conceptFinder._loadCSV(file)
    file = './data/CIE-10.txt'
    conceptFinder._loadCSV(file)
    conceptFinder.serialize('./data/serialize.dat' )
    print('Cargados los diccionarios.')

if ENABLE_GRAPH:
    umls_graph = graph.loadUMLSGraph()

@app.route("/")
def hello():
    return "Buscador Semántico Biomédico - Backend"

def cleanHtml(html):
  html = html.replace('\n', ' ')
  cleanr = re.compile('<.*?>')
  return re.sub(cleanr, '', html)

def searchBetweenPositions(begin, end, list_of_dictionaries):
  return [element for element in list_of_dictionaries if element['begin'] <= begin and element['end'] >= end]

def removeTermsInsideTerms(dic_concept):
  list_final = []
  for index, item in enumerate(dic_concept):
    list_return = searchBetweenPositions(item['begin'], item['end'], dic_concept)
    if len(list_return) == 1:
      list_final.append(item)

  return list_final

def getNER(dic_concept, text):
  list_ner = []
  for item in dic_concept:
    begin = item['begin']
    end = item['end']
    concept = text[begin:end]
    list_ner.append(concept.lower())

  list_ner = list(set(list_ner))
  string_ner = ' '.join(list_ner)
  return list_ner, string_ner


def searchDictionaries(key, value, list_of_dictionaries):
    return next((element for element in list_of_dictionaries if element[key] == value), False)


# -----------------------------------------------------------------------------
# BÚSQUEDA DE CONCEPTOS EN DICCIONARIOS
# -----------------------------------------------------------------------------
def getTerms(text):
  '''
  Devuelve, a partir de un texto dado, los conceptos encontrados
  '''
  global conceptFinder


  list_postagger = SyntacticAnalysis.analysisSpa(text)
  list_term_dic = conceptFinder.search(text)
  list_term_dic = removeTermsInsideTerms(list_term_dic)
  list_term_dic = SyntacticAnalysis.getLisNouns(list_postagger, list_term_dic)

  return list_term_dic


def obtainCodes(data):
  data_str = ''
  for d in data:
      if 'medline' in d:
        list_data = d.split('/')
        number = list_data[len(list_data)-1].split('.')[0]
        data_str += "Medline: <a href='https://medlineplus.gov/spanish/ency/article/"+number+".htm' target='_blank'>" + number + "</a>"
      elif 'UMLS' in d:
        cui = d.split(':')[1]
        data_str += "UMLS: "+ cui
      elif 'CIE' in d:
        cui = d.split(':')[1]
        code = cui[:4]
        data_str += "CIE-10: <a href='http://eciemaps.msssi.gob.es/ecieMaps/browser/index_10_2008.html#search="+code.strip()+"' target='_blank'>" + cui + "</a>"
      else:
        data_str += d
      data_str += "<br/>"

  return data_str

def getParsedText(text, list_terms):
  '''
  Produced the HTML output that will display the parsed text (that with
  entities marked)
  '''
  text += ' '
  html = '';
  for position, word in enumerate(text):
    if searchDictionaries('begin', position, list_terms):

      dic_concept = searchDictionaries('begin', position, list_terms)
      begin = dic_concept['begin']
      end = dic_concept['end']
      concept = text[begin:end]
      data = dic_concept['data']
      data_str = obtainCodes(data)

      html += '<a href="#" class="badge badge-success entity" data-toggle="popover"' + \
        ' title="' + concept + '"' + \
        ' data-content="' + data_str + '" data-html="true" data-trigger="focus">' + word

    elif searchDictionaries('end', position, list_terms):
      html += '</a>' + word

    else:
      html += word

  return html

@app.route("/parse", methods=['POST'])
def parse():

  # Processing incoming text
  text = request.form.get('t')
  text = urllib.parse.unquote(base64.b64decode(text).decode('utf-8'))
  text = cleanHtml(text)

  global list_ner
  global string_ner

  list_ner = []
  string_ner = ""
  parsed_text = text

  if ENABLE_SEARCH:
    list_terms = getTerms(text)
    list_ner, string_ner = getNER(list_terms, text)
    parsed_text = getParsedText(text, list_terms)
    myPath = os.getcwd() + '/data/'
    files = [myPath.strip() +'Medline.txt', myPath.strip() +'CIE-10.txt', myPath.strip() +'UMLS_concept.txt']
    dic_sy = SearchCUIS.search(list_terms, files)

  return render_template('parsed_content.html', dic_sy=dic_sy , parsed_text=parsed_text)

# -----------------------------------------------------------------------------
# Google Scholar
# -----------------------------------------------------------------------------

def parseHtmlScholar(list_scholar):
  '''
  Dado un resultado devuelto por la API, genera el HTML propio
  '''
  html = ''

  for item in list_scholar:
    if 'title' in item:
      if 'url' in item:
        html += '<a href="' + item['url'] + '" target="_blank"><span style="font-family:Helvetica;font-size:14px;">' + item['title'] + '</span></a>'
      else:
        html += item['title']
      if 'author' in item:
        html += '<br/><span style="color:#006621;font-family:Helvetica;font-size:14px;">' +  item['author'] +'</span>'
      if 'abstract' in item:
         html += '<br/><span style="font-family:Helvetica;font-size:14px;">' + item['abstract'] + '</span>'
      if 'citedby' in item :
        html += '<br/><span style="font-family:Helvetica;font-size:14px;">Citado por ' + item['citedby'] +'</span>'
    html += '<p/>'

  return html


@app.route("/scholar")
def scholar():

  print("\nBusqueda en Google: ", string_ner)
  if ENABLE_SCHOLAR:
    list_scholar = GoogleScholar.googleScholar(string_ner, 10)
    scholar_result = parseHtmlScholar(list_scholar)

    return scholar_result
  return ""

@app.route("/updateEntities", methods=["POST"])
def test():
  global list_ner
  list_ner= request.get_json()

  global string_ner
  string_ner = ' '.join(list_ner)
  return ""

# -----------------------------------------------------------------------------
# MEDLINE
# -----------------------------------------------------------------------------

def parseHtmlWSMedline(list_medline):
  html = ''
  for item in list_medline:
    if 'title' in item and 'key' in item:
      html += '<b><a href="'+ item['key']+'" target="_blank"><span style="font-family:Helvetica;font-size:14px;">' + item['title'] + '</span></a></b>'
      if 'organizationName' in item:
        html += ' <span style="color:#006621;font-family:Helvetica;font-size:14px;">(' + item['organizationName'] + ')</span>'
      if 'snippet' in item:
         html += '<br/><span style="font-family:Helvetica;font-size:14px;">' + item['snippet'] + '</span>'

    html += '<p/>'

  return html

@app.route("/medline")
def medline():
  if ENABLE_MEDLINE:
    print("\nBúsqueda en Medline: ", list_ner)
    list_medline = ws_medliplus.search(list_ner, 10)
    medline_result = parseHtmlWSMedline(list_medline)
    return medline_result
  return ""


# -----------------------------------------------------------------------------
# SCIELO
# -----------------------------------------------------------------------------

def parseHtmlScielo(list_scielo):
  html = ''
  for item in list_scielo:
    if 'title' in item and 'url' in item:
      html += '<b><a href="'+ item['url']+'" target="_blank"><span style="font-family:Helvetica;font-size:14px;">' + item['title'] + '</span></a></b>'
      if 'text' in item:
         html += '<br/><span style="font-family:Helvetica;font-size:14px;">...' + item['text'] + '<span style="font-family:Helvetica;font-size:14px;">'
    html += '<p/>'

  return html

@app.route("/scielo")
def scielo():
  if ENABLE_SCIELO:
    print("\nBúsqueda en Scielo: ", string_ner)
    list_scielo = search_scielo.search(string_ner, 10)
    scielo_result = parseHtmlScielo(list_scielo)
    return scielo_result
  return ""

# -----------------------------------------------------------------------------
# Graph nodes
# -----------------------------------------------------------------------------

@app.route("/graph", methods=['POST'])
def graph():

  nodes = request.get_json()

  if ENABLE_GRAPH:
    graph_data = graph.subgraph(umls_graph, nodes)
    return jsonify(graph_data);

  return jsonify([]);

# -----------------------------------------------------------------------------
# PROXY para poder mostrar páginas que no permiten ser embebidas en marcos
# -----------------------------------------------------------------------------

@app.route("/proxy")
def proxy():
  link = request.args.get('url')
  #~ f = urllib.urlopen(link)
  f = urllib.request.urlopen(link)
  html_result = f.read().decode('utf-8').replace("<script", "<!-- script").replace("</script>", "</script -->")
  return html_result


@app.route("/form", methods=["POST"])
def formulario():
  list_ner= request.form['ners']
  print(list_ner)

  return ""
