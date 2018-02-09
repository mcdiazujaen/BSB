#!/usr/bin/env python
# -*- coding: utf-8 -*-

class SearchCUIS:
	def search(lis_dic, list_files):

		dic_sy = {}
		for file in list_files:
			f = open(file, 'r')
			#print("Open" , file)
			content = f.readlines()
			for item in lis_dic:
				termino = item['concept']
				#si existe el término como clave
				if termino in dic_sy.keys():
					list_codes = dic_sy[termino]
				else:
					dic_sy[termino] = []
					list_codes = dic_sy[termino]
				for ids in item['data']:
					if "UMLS" in ids or "Snomed" in ids or "CIE" in ids:
						code = ids.split(':')[1]
						code = ';'+code.strip()
						#print(code)
						matching = [s for s in content if code in s]
						for match in matching:
							#print(match)
							concept = match.split(';')[0].strip().lower()
							list_codes.append(concept)
						
				list_codes = list(set(list_codes))
				
				dic_sy[termino]	= list_codes
			f.close()
		
		return dic_sy
