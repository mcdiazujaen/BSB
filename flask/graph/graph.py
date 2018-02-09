import networkx as nx
import os

def loadUMLSGraph():
    G = nx.Graph()
    script_dir = os.path.dirname(__file__)
    filepath = os.path.join('../data', 'relations.txt')
    with open(filepath) as f:
        for line in f[:1000]:
            t = line.split(';')
            # relation = re.split(r'([^_]+)_(.*)', t[1])
            # if (len(relation[2]) > 0):
            #     relation = relation[2]
            # else:
            #     relation = relation[1]
            relation = t[1]
            G.add_nodes_from([t[0], t[2]])
            G.add_edge(t[0], t[2], label=relation)
    return G

def subgraph(G, nodes):
  Gs = nx.Graph()
  for i in range(len(nodes)):
    for j in range(i+1, len(nodes)):
      Gs.add_path(nx.shortest_path(G, nodes[i], nodes[j]))
  return Gs


# #!/usr/bin/env python
# #import matplotlib.pyplot as plt
#
# # Generamos un grafo cualquiera
# G = nx.ladder_graph(15)
# pos=nx.spring_layout(G)
# nx.draw_networkx_labels(G, pos)
# nx.draw_networkx_edges(G, pos)
# plt.show()
#
# # Nos quedamos con el subgrafo que contiene los nodos indicados
# nodes = [1, 5, 8, 3]
# Gs = nx.Graph()
# for i in range(len(nodes)):
#     for j in range(i+1, len(nodes)):
#         Gs.add_path(nx.shortest_path(G, nodes[i], nodes[j]))
#
# pos=nx.spring_layout(Gs)
# nx.draw_networkx_labels(Gs, pos)
# nx.draw_networkx_edges(Gs, pos)
# plt.show()
