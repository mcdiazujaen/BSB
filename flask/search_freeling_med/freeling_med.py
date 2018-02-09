import subprocess
import xml.etree.ElementTree as ET
import os
import sys
import shutil

#---------------------------------------------------------
# Funciones para el fichero para la salida

def output_init(file_output_name):
    orig_stdout = sys.stdout
    f = open(file_output_name, 'w')
    sys.stdout = f
    return f, orig_stdout
#---------------------------------------------------------

def output_end(f , orig_stdout):
    sys.stdout = orig_stdout
    f.close()

#---------------------------------------------------------
#    Función para leer las etiquetas <externalRef>   
def get_external_reference(exRef, dic_text, id, list_terms):

    dic_id = dic_text[id]
    list_data = []
    for reference in exRef:
        resource = reference.get('resource')
        ref = reference.get('reference')
        data = str(resource) + ": " + str(ref) + '<\n'
        list_data.append(data)    
        for e in reference.findall("externalRef"):
            resource = e.get('resource')
            ref = e.get('reference')
            data = str(resource) + ": " + str(ref) + '<\n'
            list_data.append(data)    
    
    list_data = list(set(list_data))
    begin = int(dic_id['offset'])
    end =  int(dic_id['offset']) + int(dic_id['lenght'])
    concept = dic_id['concept']
    dic_tem = {'begin': begin, 'end': end, 'concept': concept, 'data': list_data}
    list_terms.append(dic_tem)
    
#---------------------------------------------------------
# Función para leer cada etiqueta <externalReferences>
def get_external_references(externalReferences, dic_text, id, list_terms):
    for externalReference in externalReferences:
        externalRef = externalReference.findall("externalRef")
        if len(externalRef) > 0:
            get_external_reference(externalRef, dic_text, id, list_terms)

#---------------------------------------------------------
#   Función para leer las etiquetas <span> que es donde se encuentran los ids
#   y posiciones de cada término reconocido
def get_span(term, dic_text):
    span =term.find("span")
    if not span is None:
        target = span.find("target")
        if not target is None:
            id= target.get("id")
            if id in dic_text:
                return id

#---------------------------------------------------------
#   Función para leer las etiquetas <wf> que es donde se encuentran los ids
#   y posiciones de cada palabra del texto       
def get_text_wf(root):
    dic_text = {}
    for wf in root.iter('wf'):
        id = wf.get('id')
        length = wf.get('length')
        offset = wf.get('offset')
        concept = wf.text#('length')
        dic_text[id]={'lenght': length, 'offset': offset, 'concept': concept}
    return dic_text

#---------------------------------------------------------             
# Función para leer cada fichero y tratarlo como XML
def read_file(file):
    tree = ET.parse(file)
    root = tree.getroot()
    dic_text = get_text_wf(root)
    list_terms = []
    for term in root.iter('term'):
        externalReferences = term.findall("externalReferences")
        if len(externalReferences) > 0:
            id = get_span(term, dic_text)
            get_external_references(externalReferences, dic_text, id, list_terms)
    
    return list_terms

#---------------------------------------------------------   
# Función para leer los ficheros generados por freelingMed   
def read_path(path):      
    list_terms = []
    for base, dirs, files in os.walk(path):
        filesXML = [x for x in files if str(x).endswith(".naf")]
        if len(filesXML) >0 :
            for file in filesXML:        
                list_terms = read_file(base + '/' + file)

    return list_terms
#---------------------------------------------------------
# Función que crea el directorio para trabajar freelingMed
def create_file(path, text):
    if os.path.isdir(path):
    	remove_files(path)

    os.mkdir(path)    
    file = open(path + '/myfile.txt', 'w')
    file.write(text)
    file.close()

#---------------------------------------------------------
# Función que elimina todos los fichero generados por freelingMed
def remove_files(path):
	if os.path.isdir(path):
		shutil.rmtree(path)

#---------------------------------------------------------
# Función principal
def search_freelingmed(text):
#if __name__ == '__main__':

	#Param1: nombre del fichero de salida
	#file_output_name = sys.argv[1]

	#Param2: cadena de texto a tratar
	#text = sys.argv[1]
	 
	# Inicio fichero de salida      
	#file_output, orig_stdout = output_init(file_output_name)
    command = 'bash'
    file_exe_freelingmed = os.getcwd()+ '/search_freeling_med/dir_naf.sh'
    path = './prueba'

    create_file(path, text)
    subprocess.call([command, file_exe_freelingmed, path])
	
    list_terms = read_path(path)
    remove_files(path)
	
    return list_terms

	# Cierre del fichero de salida
	#output_end( file_output, orig_stdout )
