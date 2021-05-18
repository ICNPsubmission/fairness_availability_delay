import networkx as nx
import matplotlib.pyplot as plt
import os
import geopy.distance
import random
import math

def generate_graph(file):
    topology_dataset_path = r'(path to gml graphs folder)'
    G=nx.read_gml(os.path.join(topology_dataset_path, file))
    #MTBF and MTTR values are based on the mathematical model in Facebook's IMC'18 paper "A Large Scale Study of Data Center Network Reliability"
    MTBF_percentile_1 = 336.51 * math.exp(3.4371 * float(1) / 100)
    MTBF_percentile_99 = 336.51 * math.exp(3.4371 * float(99) / 100)
    MTTR_percentile_1 = 1.1345 * math.exp(4.7709 * float(1) / 1000)
    MTTR_percentile_99 = 1.1345 * math.exp(4.7709 * float(99) / 1000)
    for (u, v) in G.edges():
        coords_1 = (G.node[u]['Latitude'],G.node[u]['Longitude'])
        coords_2 = (G.node[v]['Latitude'], G.node[v]['Longitude'])
        G.edges[u, v]['latency'] = geopy.distance.distance(coords_1, coords_2).km/50 # latency 1km= 0.5 ms
        G.edges[u, v]['capacity'] = random.randint(50, 100)  # Gbps
        MTBF = random.uniform(MTBF_percentile_1, MTBF_percentile_99)
        MTTR = random.uniform(MTTR_percentile_1, MTTR_percentile_99)
        G.edges[u, v]['availability'] = MTBF/(MTTR+MTBF)  # fraction
    nx.draw(G, with_labels=True, node_color='y')
    plt.show()
    return G


